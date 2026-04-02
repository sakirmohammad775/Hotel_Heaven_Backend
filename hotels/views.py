from hotels.models import Hotel, Category, Review, HotelImage
from hotels.serializers import (
    HotelSerializer, CategorySerializer,
    ReviewSerializer, HotelImageSerializer
)
from django.db.models import Count
from rest_framework.viewsets import ModelViewSet
from django_filters.rest_framework import DjangoFilterBackend
from hotels.filters import HotelFilter
from rest_framework.filters import SearchFilter, OrderingFilter
from hotels.paginations import DefaultPagination
from api.permissions import IsAdminOrReadOnly
from hotels.permissions import IsReviewAuthorOrReadonly
from drf_yasg.utils import swagger_auto_schema

## For AI implementation


class HotelViewSet(ModelViewSet):
    serializer_class = HotelSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = HotelFilter
    pagination_class = DefaultPagination
    search_fields = ['name', 'description', 'location']
    ordering_fields = ['price', 'updated_at']
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        return Hotel.objects.prefetch_related('images').all()

    @swagger_auto_schema(operation_summary='Retrieve hotels')
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary="Create hotel")
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)


class HotelImageViewSet(ModelViewSet):
    serializer_class = HotelImageSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        return HotelImage.objects.filter(
            hotel_id=self.kwargs.get('hotel_pk')
        )

    def perform_create(self, serializer):
        serializer.save(hotel_id=self.kwargs.get('hotel_pk'))


class CategoryViewSet(ModelViewSet):
    permission_classes = [IsAdminOrReadOnly]
    queryset = Category.objects.annotate(
        hotel_count=Count('hotels')
    ).all()
    serializer_class = CategorySerializer


class ReviewViewSet(ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [IsReviewAuthorOrReadonly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        return Review.objects.filter(
            hotel_id=self.kwargs.get('hotel_pk')
        )

    def get_serializer_context(self):
        return {'hotel_id': self.kwargs.get('hotel_pk')}








import os
from google import genai
from google.genai import types
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Hotel

# 1. Setup Client (Hardcode key temporarily if .env fails on Vercel)
# Use your actual key: AIzaSy...
API_KEY="AIzaSyBCSEWttnwBv3VVV2zmEA3n0FjEdjYbhzc"
client = genai.Client(api_key=API_KEY)

class ConciergeBotView(APIView):
    def post(self, request):
        # Get message safely
        user_query = request.data.get("message", "Hello")
        
        try:
            # 🔹 2. GET DATA (With fallback for empty DB)
            hotels = Hotel.objects.all()
            hotel_data = ""
            
            if not hotels.exists():
                hotel_data = "We currently have no rooms available in the registry."
            else:
                for h in hotels:
                    # Using getattr to prevent crash if a field is missing
                    name = getattr(h, 'name', 'A Luxury Suite')
                    price = getattr(h, 'price_with_tax', 'Premium Rate')
                    loc = getattr(h, 'location', 'Our Sanctuary')
                    hotel_data += f"- {name} in {loc}: ${price}/night.\n"

            # 🔹 3. THE 2026 AI CALL
            # Note: Changed to gemini-1.5-flash as it's more stable for Free Tier
            response = client.models.generate_content(
                model="gemini-1.5-flash", 
                contents=user_query,
                config=types.GenerateContentConfig(
                    system_instruction=f"You are the HotelHeaven Concierge. Available hotels: {hotel_data}. Be elegant. End with 'Your Sanctuary awaits.'"
                )
            )
            
            # Ensure we send the .text specifically
            return Response({"reply": response.text})

        except Exception as e:
            # 🛑 THIS WILL NOW SHOW YOU THE EXACT ERROR IN THE CHAT
            error_msg = f"Registry Error: {str(e)}"
            print(f"DEBUG: {error_msg}") # Check Vercel logs for this!
            return Response({"reply": error_msg}, status=200)