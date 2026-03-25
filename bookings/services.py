from bookings.models import Cart, CartItem, BookingItem, Booking
from django.db import transaction
from rest_framework.exceptions import PermissionDenied, ValidationError
from django.utils import timezone
from datetime import timedelta


class BookingService:
    @staticmethod
    def create_booking(user_id, cart_id, check_in=None, check_out=None):
        with transaction.atomic():
            cart = Cart.objects.get(pk=cart_id)
            cart_items = cart.items.select_related('hotel').all()

            total_price = sum([
                item.hotel.price * item.quantity
                for item in cart_items
            ])

            # Default: check_in = today, check_out = tomorrow
            today = timezone.now().date()
            booking = Booking.objects.create(
                user_id=user_id,
                total_price=total_price,
                check_in=check_in or today,
                check_out=check_out or (today + timedelta(days=1))
            )

            booking_items = [
                BookingItem(
                    booking=booking,
                    hotel=item.hotel,
                    price=item.hotel.price,
                    quantity=item.quantity,
                    total_price=item.hotel.price * item.quantity
                )
                for item in cart_items
            ]

            BookingItem.objects.bulk_create(booking_items)
            cart.delete()

            return booking

    @staticmethod
    def cancel_booking(booking, user):
        if user.is_staff:
            booking.status = Booking.CANCELED
            booking.save()
            return booking

        if booking.user != user:
            raise PermissionDenied(
                {"detail": "You can only cancel your own booking"})

        if booking.status == Booking.COMPLETED:
            raise ValidationError({"detail": "Cannot cancel completed booking"})

        booking.status = Booking.CANCELED
        booking.save()
        return booking