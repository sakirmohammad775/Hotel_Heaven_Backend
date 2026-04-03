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

        # ✅ 1. Validate input
        if not user_message:
            return Response(
                {"error": "Message is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        client = get_openai_client()

        # ✅ Default filters (fallback safe)
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
You are a strict JSON generator.

Extract hotel search filters from user message.

Rules:
- Return ONLY valid JSON
- No explanation, no extra text
- If not found → use null
- Always include all keys

Keys:
- location (string)
- max_price (number)
- min_price (number)
- rooms (number)

Examples:

Input: cheap hotel in Cox's Bazar under 200
Output:
{
  "location": "Cox's Bazar",
  "max_price": 200,
  "min_price": null,
  "rooms": null
}

Input: hotel in dhaka above 100 with 2 rooms
Output:
{
  "location": "Dhaka",
  "max_price": null,
  "min_price": 100,
  "rooms": 2
}
"""
                        },
                        {"role": "user", "content": user_message},
                    ],
                )

                raw_output = ai_response.choices[0].message.content.strip()

                # ✅ Remove markdown if exists
                raw_output = raw_output.replace("```json", "").replace("```", "").strip()

                parsed = json.loads(raw_output)

                # ✅ Safe assign (avoid missing keys)
                filters["location"] = parsed.get("location")
                filters["max_price"] = parsed.get("max_price")
                filters["min_price"] = parsed.get("min_price")
                filters["rooms"] = parsed.get("rooms")

            except Exception as e:
                print("❌ AI ERROR:", e)

        # ================================
        # 🧠 DEBUG (VERY IMPORTANT)
        # ================================
        print("USER MESSAGE:", user_message)
        print("AI FILTERS:", filters)

        # ================================
        # 🧠 STEP 2: Django Filtering
        # ================================
        queryset = Hotel.objects.all()

        location = filters.get("location")
        max_price = filters.get("max_price")
        min_price = filters.get("min_price")
        rooms = filters.get("rooms")

        if location:
            queryset = queryset.filter(location__icontains=location)

        if max_price is not None:
            queryset = queryset.filter(price__lte=max_price)

        if min_price is not None:
            queryset = queryset.filter(price__gte=min_price)

        if rooms is not None:
            queryset = queryset.filter(available_rooms__gte=rooms)

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

        # ✅ Dynamic message
        message = f"Found {len(results)} hotels"

        if location:
            message += f" in {location}"
        if max_price:
            message += f" under {max_price}"
        if min_price:
            message += f" above {min_price}"

        return Response({
            "filters": filters,
            "results": results,
            "message": message
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
