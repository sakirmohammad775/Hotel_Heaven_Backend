from django.urls import path, include
from hotels.views import HotelViewSet, CategoryViewSet, ReviewViewSet, HotelImageViewSet
from bookings.views import CartViewSet, CartItemViewSet, BookingViewSet, HasBookedHotel
from rest_framework_nested import routers

# MAIN ROUTER
router = routers.DefaultRouter()
router.register('hotels', HotelViewSet, basename='hotels')   # changed
router.register('categories', CategoryViewSet)
router.register('carts', CartViewSet, basename='carts')
router.register('bookings', BookingViewSet, basename='bookings')  # changed

# NESTED ROUTER (HOTEL → reviews, images)
hotel_router = routers.NestedDefaultRouter(
    router, 'hotels', lookup='hotel')   # changed

hotel_router.register('reviews', ReviewViewSet, basename='hotel-review')  # changed
hotel_router.register('images', HotelImageViewSet, basename='hotel-images')  # changed

# NESTED ROUTER (CART → items)
cart_router = routers.NestedDefaultRouter(router, 'carts', lookup='cart')
cart_router.register('items', CartItemViewSet, basename='cart-item')


urlpatterns = [
    path('', include(router.urls)),
    path('', include(hotel_router.urls)),
    path('', include(cart_router.urls)),

    # AUTH
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),

    # PAYMENT
    # path("payment/initiate/", initiate_payment, name="initiate-payment"),
    # path("payment/success/", payment_success, name="payment-success"),
    # path("payment/fail/", payment_fail, name="payment-fail"),
    # path("payment/cancel/", payment_cancel, name="payment-cancel"),

    # CHECK USER BOOKED HOTEL
    path('bookings/has-booked/<int:hotel_id>/',  # changed
         HasBookedHotel.as_view()),
]