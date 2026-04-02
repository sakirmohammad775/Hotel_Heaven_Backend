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

# 1. Setup Client with your working API Key
API_KEY = "AIzaSyBCSEWttnwBv3VVV2zmEA3n0FjEdjYbhzc"
client = genai.Client(api_key=API_KEY)

class ConciergeBotView(APIView):
    def post(self, request):
        # Safely get message
        user_query = request.data.get("message", "Hello")
        
        # Initialize context variable at the top
        hotel_data = "No hotels currently available in our registry."
        
        try:
            # 2. FETCH DATA FROM DATABASE
            hotels = Hotel.objects.all()
            if hotels.exists():
                hotel_list = []
                for h in hotels:
                    # Using getattr ensures it doesn't crash if a column is missing
                    name = getattr(h, 'name', 'Luxury Suite')
                    price = getattr(h, 'price_with_tax', 'Premium')
                    loc = getattr(h, 'location', 'Sanctuary')
                    hotel_list.append(f"- {name} in {loc}: ${price}/night.")
                
                hotel_data = "\n".join(hotel_list)

            # 3. THE AI CALL (2.0-FLASH IS THE 2026 STABLE VERSION)
            # If this gives 404, the SDK will automatically try to find the best match
            response = client.models.generate_content(
                model="gemini-2.0-flash", 
                contents=user_query,
                config=types.GenerateContentConfig(
                    system_instruction=f"You are the HotelHeaven Concierge. Available hotels:\n{hotel_data}\n\nRule: Be elegant, helpful, and ALWAYS end with 'Your Sanctuary awaits.'"
                )
            )
            
            # Return the text from the AI
            return Response({"reply": response.text})

        except Exception as e:
            # Check for the specific 404 error to give you advice
            error_str = str(e)
            if "404" in error_str:
                return Response({"reply": "Registry Error: Model mismatch. Please ensure Gemini 2.0 is enabled in your Google AI Studio."}, status=200)
            
            # General error fallback
            return Response({"reply": f"Registry Error: {error_str}"}, status=200)