from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from cloudinary.models import CloudinaryField


class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class Hotel(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)  # per night
    available_rooms = models.PositiveIntegerField(default=0)

    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="hotels")

    location = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return self.name


class HotelImage(models.Model):   # ✅ updated name
    hotel = models.ForeignKey(
        Hotel, on_delete=models.CASCADE, related_name='images')
    image = CloudinaryField('image')


class Review(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    ratings = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )

    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Review by {self.user.email} on {self.hotel.name}"