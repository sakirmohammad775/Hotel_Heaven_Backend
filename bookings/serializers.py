from rest_framework import serializers
from bookings.models import Cart, CartItem, Booking, BookingItem
from hotels.models import Hotel
from bookings.services import BookingService


class EmptySerializer(serializers.Serializer):
    pass


# 🔹 Simple Hotel (like SimpleProduct)
class SimpleHotelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hotel
        fields = ["id", "name", "price"]


# 🔹 Add to Cart
class AddCartItemSerializer(serializers.ModelSerializer):
    hotel_id = serializers.IntegerField()

    class Meta:
        model = CartItem
        fields = ["id", "hotel_id", "quantity"]

    def save(self, **kwargs):
        cart_id = self.context["cart_id"]
        hotel_id = self.validated_data["hotel_id"]
        quantity = self.validated_data["quantity"]

        try:
            cart_item = CartItem.objects.get(cart_id=cart_id, hotel_id=hotel_id)
            cart_item.quantity += quantity
            cart_item.save()
            self.instance = cart_item
        except CartItem.DoesNotExist:
            self.instance = CartItem.objects.create(
                cart_id=cart_id, **self.validated_data
            )

        return self.instance

    def validate_hotel_id(self, value):
        if not Hotel.objects.filter(pk=value).exists():
            raise serializers.ValidationError(f"Hotel with id {value} does not exist")
        return value


class UpdateCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ["quantity"]


class CartItemSerializer(serializers.ModelSerializer):
    hotel = SimpleHotelSerializer()
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ["id", "hotel", "quantity", "total_price"]

    def get_total_price(self, obj):
        return obj.quantity * obj.hotel.price


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ["id", "user", "items", "total_price"]
        read_only_fields = ["user"]

    def get_total_price(self, cart):
        return sum([item.hotel.price * item.quantity for item in cart.items.all()])


# 🔹 Create Booking (like Order)
# Replace only the CreateBookingSerializer in your bookings/serializers.py


class CreateBookingSerializer(serializers.Serializer):
    cart_id = serializers.UUIDField()
    check_in = serializers.DateField(required=True) 
    check_out = serializers.DateField(required=True)
    # 🔹 YOU MUST ADD THIS LINE SO DJANGO ACCEPTS THE PRICE FROM REACT
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)

    def validate_cart_id(self, cart_id):
        if not Cart.objects.filter(pk=cart_id).exists():
            raise serializers.ValidationError("No cart found")
        return cart_id

    def validate(self, data):
        check_in = data.get("check_in")
        check_out = data.get("check_out")
        if check_in and check_out and check_out <= check_in:
            raise serializers.ValidationError("Check-out must be after check-in")
        return data

    def create(self, validated_data):
        user_id = self.context["user_id"]
        cart_id = validated_data["cart_id"]
        check_in = validated_data.get("check_in")
        check_out = validated_data.get("check_out")
        # Now this will actually contain the value from React
        total_price = validated_data.get("total_price") 

        try:
            return BookingService.create_booking(
                user_id=user_id,
                cart_id=cart_id,
                check_in=check_in,
                check_out=check_out,
                total_price=total_price, 
            )
        except Exception as e:
            raise serializers.ValidationError(str(e))

    def to_representation(self, instance):
        return BookingSerializer(instance).data

class BookingItemSerializer(serializers.ModelSerializer):
    hotel = SimpleHotelSerializer()

    class Meta:
        model = BookingItem
        fields = ["id", "hotel", "price", "quantity", "total_price"]


class UpdateBookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ["status"]


class BookingSerializer(serializers.ModelSerializer):
    items = BookingItemSerializer(many=True)
    user_email = serializers.EmailField(source='user.email', read_only=True, default="Guest")
    class Meta:
        model = Booking
        fields = [
            "id", "user","user_email", "status", "total_price", 
            "check_in", "check_out", "created_at", "items"
        ]