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