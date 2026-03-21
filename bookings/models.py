from django.db import models
from django.core.validators import MinValueValidator
from users.models import User
from hotels.models import Hotel
from uuid import uuid4


class Cart(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="cart")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart of {self.user.email}"


class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart, on_delete=models.CASCADE, related_name="items")
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])

    class Meta:
        unique_together = [['cart', 'hotel']]

    def __str__(self):
        return f"{self.quantity} x {self.hotel.name}"


class Booking(models.Model):
    NOT_PAID = 'Not Paid'
    CONFIRMED = 'Confirmed'
    CHECKED_IN = 'Checked In'
    COMPLETED = 'Completed'
    CANCELED = 'Canceled'

    STATUS_CHOICES = [
        (NOT_PAID, 'Not Paid'),
        (CONFIRMED, 'Confirmed'),
        (CHECKED_IN, 'Checked In'),
        (COMPLETED, 'Completed'),
        (CANCELED, 'Canceled')
    ]

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="bookings")

    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default=NOT_PAID)

    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    check_in = models.DateField()
    check_out = models.DateField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Booking {self.id} by {self.user.email} - {self.status}"


class BookingItem(models.Model):
    booking = models.ForeignKey(
        Booking, on_delete=models.CASCADE, related_name="items")
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE)

    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.hotel.name}"