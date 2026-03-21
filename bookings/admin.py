from django.contrib import admin
from bookings.models import Cart, CartItem, Booking, BookingItem


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['id', 'user']


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'status']


admin.site.register(CartItem)
admin.site.register(BookingItem)