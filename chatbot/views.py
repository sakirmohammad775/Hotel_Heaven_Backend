import os
import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from openai import OpenAI
from hotels.models import Hotel


def get_openai_client():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None
    return OpenAI(api_key=api_key)


class ChatBotView(APIView):
    def post(self, request):
        user_message = request.data.get("message")

        # ✅ Validate input
        if not user_message:
            return Response(
                {"error": "Message is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        client = get_openai_client()

        filters = {
            "location": None,
            "max_price": None,
            "min_price": None,
            "rooms": None,
        }

        # ================================
        # 🧠 STEP 1: AI → Extract Filters
        # ================================
        if client:
            try:
                ai_response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {
                            "role": "system",
                            "content": """
Extract hotel search filters from user message.

Return ONLY valid JSON:
{
  "location": string or null,
  "max_price": number or null,
  "min_price": number or null,
  "rooms": number or null
}
""",
                        },
                        {"role": "user", "content": user_message},
                    ],
                    temperature=0,
                )

                raw_output = ai_response.choices[0].message.content.strip()

                # ✅ Clean possible bad formatting
                raw_output = raw_output.replace("```json", "").replace("```", "").strip()

                filters = json.loads(raw_output)

            except Exception as e:
                print("AI ERROR:", e)

        # ================================
        # 🧠 STEP 2: Django Filtering
        # ================================
        queryset = Hotel.objects.all()

        if filters.get("location"):
            queryset = queryset.filter(location__icontains=filters["location"])

        if filters.get("max_price"):
            queryset = queryset.filter(price__lte=filters["max_price"])

        if filters.get("min_price"):
            queryset = queryset.filter(price__gte=filters["min_price"])

        if filters.get("rooms"):
            queryset = queryset.filter(available_rooms__gte=filters["rooms"])

        queryset = queryset[:5]

        # ================================
        # 🧠 STEP 3: Format Response
        # ================================
        results = []
        for h in queryset:
            results.append({
                "id": h.id,
                "name": h.name,
                "price": float(h.price),
                "location": h.location,
                "available_rooms": h.available_rooms,
                "image": h.images.first().image.url if h.images.exists() else None,
            })

        return Response({
            "filters": filters,
            "results": results,
            "message": f"Found {len(results)} hotels"
        })
        
        
        
        





# React Chat UI
#      ↓
# Django API (/api/v1/concierge/)
#      ↓
# AI → convert message → structured filters (JSON)
#      ↓
# Django ORM filter (Hotel model)
#      ↓
# Return hotels → React UI