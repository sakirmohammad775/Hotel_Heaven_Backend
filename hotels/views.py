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
    

from google.genai import Client # This is the new package
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Hotel

# Initialize the client (Better to put the key in your settings.py or .env)
client = Client(api_key="AIzaSyAYlzIHiH3xNnhifLWEq5Yj20NMYj_Aodk")

class ConciergeBotView(APIView):
    def post(self, request):
        user_query = request.data.get("message")
        
        # 1. Fetch your hotels from DB
        hotels = Hotel.objects.all()
        
        # 2. Format your hotel knowledge base
        hotel_data_str = "Available Sanctuaries at HotelHeaven:\n"
        for h in hotels:
            hotel_data_str += (
                f"- {h.name} in {h.location}: ${h.price_with_tax}/night. "
                f"Description: {h.description} Rooms left: {h.available_rooms}\n"
            )

        # 3. Use the NEW 'models.generate_content' syntax
        system_instructions = f"""
        You are the 'Heavenly Concierge' for HotelHeaven. 
        Tone: Professional, sophisticated, and minimalist.
        
        Knowledge Base:
        {hotel_data_str}
        
        Rules:
        - Only suggest hotels from the list above.
        - If asked for pricing, always use the price_with_tax value.
        - End every response with 'Your Sanctuary awaits.'
        """

        try:
            response = client.models.generate_content(
                model="gemini-2.0-flash", # You can now use the latest 2.0 models!
                contents=f"{system_instructions}\n\nGuest Request: {user_query}"
            )
            
            return Response({
                "reply": response.text,
                "status": "success"
            })
        except Exception as e:
            print(f"AI Error: {e}")
            return Response({"reply": "My apologies, the registry is momentarily silent."}, status=500)