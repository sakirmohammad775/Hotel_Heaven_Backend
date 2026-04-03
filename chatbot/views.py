import os
import re
import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from hotels.models import Hotel


def extract_filters_with_keywords(message):
    """Fallback filter extractor using regex — no AI needed."""
    msg = message.lower()
    filters = {
        "location": None,
        "max_price": None,
        "min_price": None,
        "rooms": None,
    }

    # Location detection
    locations = ["cox's bazar", "coxs bazar", "cox bazar",
                 "dhaka", "chittagong", "chattogram", "sylhet"]
    for loc in locations:
        if loc in msg:
            # normalize
            if "cox" in loc:
                filters["location"] = "Cox's Bazar"
            elif "chattogram" in loc or "chittagong" in loc:
                filters["location"] = "Chattogram"
            elif "dhaka" in loc:
                filters["location"] = "Dhaka"
            elif "sylhet" in loc:
                filters["location"] = "Sylhet"
            break

    # Price: "under 200", "below 150", "less than 300"
    match = re.search(r'(under|below|less than|max|upto|up to)\s*\$?(\d+)', msg)
    if match:
        filters["max_price"] = int(match.group(2))

    # Price: "above 100", "over 100", "more than 100", "minimum 100"
    match = re.search(r'(above|over|more than|min|minimum|from)\s*\$?(\d+)', msg)
    if match:
        filters["min_price"] = int(match.group(2))

    # Rooms: "2 rooms", "at least 3 rooms"
    match = re.search(r'(\d+)\s*rooms?', msg)
    if match:
        filters["rooms"] = int(match.group(1))

    return filters


def extract_filters_with_ai(message):
    """Use OpenAI if key available."""
    try:
        from openai import OpenAI
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return None

        client = OpenAI(api_key=api_key)
        ai_response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": """Extract hotel search filters from user message.
Return ONLY valid JSON with these keys:
- location (string or null)
- max_price (number or null)
- min_price (number or null)
- rooms (number or null)

No explanation. No markdown. Just JSON."""
                },
                {"role": "user", "content": message},
            ],
        )
        raw = ai_response.choices[0].message.content.strip()
        raw = raw.replace("```json", "").replace("```", "").strip()
        return json.loads(raw)

    except Exception as e:
        print("AI extraction failed:", e)
        return None


class ChatBotView(APIView):

    def post(self, request):
        user_message = request.data.get("message", "").strip()

        if not user_message:
            return Response(
                {"error": "Message is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # ── Try AI first, fall back to keyword regex ──────────────
        parsed = extract_filters_with_ai(user_message)
        if not parsed:
            parsed = extract_filters_with_keywords(user_message)
            source = "keyword"
        else:
            source = "ai"

        filters = {
            "location":  parsed.get("location"),
            "max_price": parsed.get("max_price"),
            "min_price": parsed.get("min_price"),
            "rooms":     parsed.get("rooms"),
        }

        print(f"[{source.upper()}] Message: {user_message}")
        print(f"[{source.upper()}] Filters: {filters}")

        # ── Django ORM filtering ───────────────────────────────────
        queryset = Hotel.objects.prefetch_related("images").all()

        if filters["location"]:
            queryset = queryset.filter(location__icontains=filters["location"])
        if filters["max_price"] is not None:
            queryset = queryset.filter(price__lte=filters["max_price"])
        if filters["min_price"] is not None:
            queryset = queryset.filter(price__gte=filters["min_price"])
        if filters["rooms"] is not None:
            queryset = queryset.filter(available_rooms__gte=filters["rooms"])

        queryset = queryset[:5]

        # ── Serialize ──────────────────────────────────────────────
        results = []
        for h in queryset:
            first_image = h.images.first()
            results.append({
                "id":              h.id,
                "name":            h.name,
                "description":     h.description,
                "price":           float(h.price),
                "price_with_tax":  round(float(h.price) * 1.10, 2),
                "location":        h.location,
                "available_rooms": h.available_rooms,
                "image": first_image.image.url if first_image else None,
            })

        # ── Build message ──────────────────────────────────────────
        if results:
            msg = f"Found {len(results)} hotel{'s' if len(results) > 1 else ''}"
            if filters["location"]: msg += f" in {filters['location']}"
            if filters["max_price"]: msg += f" under ${filters['max_price']}"
            if filters["min_price"]: msg += f" above ${filters['min_price']}"
        else:
            msg = "No hotels found matching your criteria. Try different filters."

        return Response({
            "message": msg,
            "filters": filters,
            "results": results,
            "source":  source,
        })