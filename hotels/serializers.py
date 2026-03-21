from rest_framework import serializers
from decimal import Decimal
from hotels.models import Category, Hotel, Review, HotelImage
from django.contrib.auth import get_user_model


class CategorySerializer(serializers.ModelSerializer):
    hotel_count = serializers.IntegerField(
        read_only=True, help_text="Number of hotels in this category")

    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'hotel_count']


class HotelImageSerializer(serializers.ModelSerializer):
    image = serializers.ImageField()

    class Meta:
        model = HotelImage
        fields = ['id', 'image']


class HotelSerializer(serializers.ModelSerializer):
    images = HotelImageSerializer(many=True, read_only=True)
    price_with_tax = serializers.SerializerMethodField()

    class Meta:
        model = Hotel
        fields = ['id', 'name', 'description', 'price',
                  'available_rooms', 'category', 'location',
                  'price_with_tax', 'images']

    def get_price_with_tax(self, hotel):
        return round(hotel.price * Decimal(1.1), 2)

    def validate_price(self, price):
        if price < 0:
            raise serializers.ValidationError('Price cannot be negative')
        return price


class SimpleUserSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    class Meta:
        model = get_user_model()
        fields = ['id', 'name']

    def get_name(self, obj):
        return obj.get_full_name()


class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = ['id', 'user', 'hotel', 'ratings', 'comment']
        read_only_fields = ['user', 'hotel']

    def get_user(self, obj):
        return SimpleUserSerializer(obj.user).data

    def create(self, validated_data):
        hotel_id = self.context['hotel_id']
        return Review.objects.create(hotel_id=hotel_id, **validated_data)