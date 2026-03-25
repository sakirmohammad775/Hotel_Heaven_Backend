from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin, DestroyModelMixin
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from bookings import serializers as bookingSz
from bookings.serializers import (
    CartSerializer, CartItemSerializer,
    AddCartItemSerializer, UpdateCartItemSerializer
)
from bookings.models import Cart, CartItem, Booking
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.decorators import action, api_view,permission_classes
from bookings.services import BookingService
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from sslcommerz_lib import SSLCOMMERZ
from rest_framework.decorators import api_view
from django.http import HttpResponseRedirect
from django.conf import settings as main_settings
from rest_framework.permissions import IsAuthenticated

# 🔹 Cart View
class CartViewSet(CreateModelMixin, RetrieveModelMixin, DestroyModelMixin, GenericViewSet):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        return Cart.objects.prefetch_related('items__hotel').filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        existing_cart = Cart.objects.filter(user=request.user).first()

        if existing_cart:
            serializer = self.get_serializer(existing_cart)
            return Response(serializer.data, status=status.HTTP_200_OK)

        return super().create(request, *args, **kwargs)


# 🔹 Cart Item View
class CartItemViewSet(ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AddCartItemSerializer
        elif self.request.method == 'PATCH':
            return UpdateCartItemSerializer
        return CartItemSerializer

    def get_serializer_context(self):
        return {'cart_id': self.kwargs.get('cart_pk')}

    def get_queryset(self):
        return CartItem.objects.select_related('hotel').filter(
            cart_id=self.kwargs.get('cart_pk')
        )


# 🔹 Booking View
class BookingViewSet(ModelViewSet):
    http_method_names = ['get', 'post', 'delete', 'patch', 'head', 'options']

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        booking = self.get_object()
        BookingService.cancel_booking(booking=booking, user=request.user)
        return Response({'status': 'Booking canceled'})

    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        booking = self.get_object()
        serializer = bookingSz.UpdateBookingSerializer(
            booking, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'status': f"Booking updated to {request.data['status']}"})

    def get_permissions(self):
        if self.action in ['update_status', 'destroy']:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == 'cancel':
            return bookingSz.EmptySerializer
        if self.action == 'create':
            return bookingSz.CreateBookingSerializer
        elif self.action == 'update_status':
            return bookingSz.UpdateBookingSerializer
        return bookingSz.BookingSerializer

    def get_serializer_context(self):
        return {
            'user_id': self.request.user.id,
            'user': self.request.user
        }

    def get_queryset(self):
        if self.request.user.is_staff:
            return Booking.objects.prefetch_related('items__hotel').all()
        return Booking.objects.prefetch_related('items__hotel').filter(
            user=self.request.user
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])   # ← add this line only
def initiate_payment(request):
    user = request.user
    amount = request.data.get("amount")
    booking_id = request.data.get("bookingId")
    num_items = request.data.get("numItems")

    settings = {
        'store_id': 'your_store_id',
        'store_pass': 'your_store_pass',
        'issandbox': True
    }

    sslcz = SSLCOMMERZ(settings)

    post_body = {
        'total_amount': str(amount),   # ← str() wrap only, SSLCommerz needs string
        'currency': "BDT",
        'tran_id': f"txn_{booking_id}",
        'success_url': f"{main_settings.BACKEND_URL}/api/v1/payment/success/",
        'fail_url': f"{main_settings.BACKEND_URL}/api/v1/payment/fail/",
        'cancel_url': f"{main_settings.BACKEND_URL}/api/v1/payment/cancel/",
        'emi_option': 0,
        'cus_name': f"{user.first_name} {user.last_name}",
        'cus_email': user.email,
        'cus_phone': user.phone_number,
        'cus_add1': user.address,
        'cus_city': "Dhaka",
        'cus_country': "Bangladesh",
        'shipping_method': "NO",
        'multi_card_name': "",
        'num_of_item': num_items,
        'product_name': "Hotel Booking",
        'product_category': "Hotel",
        'product_profile': "general"
    }

    response = sslcz.createSession(post_body)

    if response.get("status") == 'SUCCESS':
        return Response({"payment_url": response['GatewayPageURL']})

    return Response(
        {"error": "Payment initiation failed"},
        status=status.HTTP_400_BAD_REQUEST
    )
@api_view(['POST'])
def payment_success(request):
    """SSLCommerz calls this after successful payment"""
    tran_id = request.data.get("tran_id", "")  # e.g. "txn_42"
    
    try:
        # Extract booking_id from tran_id (format: txn_{booking_id})
        booking_id = tran_id.replace("txn_", "")
        booking = Booking.objects.get(id=booking_id)
        booking.is_paid = True
        booking.status = "confirmed"
        booking.save()
        
        # Redirect to frontend success page
        return HttpResponseRedirect(f"{main_settings.FRONTEND_URL}/dashboard/bookings?payment=success")
    
    except Booking.DoesNotExist:
        return HttpResponseRedirect(f"{main_settings.FRONTEND_URL}/dashboard/bookings?payment=failed")
 
 
@api_view(['POST'])
def payment_fail(request):
    """SSLCommerz calls this on payment failure"""
    tran_id = request.data.get("tran_id", "")
    try:
        booking_id = tran_id.replace("txn_", "")
        booking = Booking.objects.get(id=booking_id)
        booking.status = "failed"
        booking.save()
    except Booking.DoesNotExist:
        pass
    return HttpResponseRedirect(f"{main_settings.FRONTEND_URL}/checkout?payment=failed")
 
 
@api_view(['POST'])
def payment_cancel(request):
    """SSLCommerz calls this on payment cancel"""
    return HttpResponseRedirect(f"{main_settings.FRONTEND_URL}/checkout?payment=cancelled")
 
 


# 🔹 Check if user booked hotel (for review permission)
class HasBookedHotel(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, hotel_id):
        user = request.user
        has_booked = Booking.objects.filter(
            user=user,
            items__hotel_id=hotel_id
        ).exists()

        return Response({"hasBooked": has_booked})