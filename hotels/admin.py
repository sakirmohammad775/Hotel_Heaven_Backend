from django.contrib import admin
from hotels.models import Hotel, Category, Review, HotelImage

admin.site.register(Hotel)
admin.site.register(HotelImage)
admin.site.register(Category)
admin.site.register(Review)