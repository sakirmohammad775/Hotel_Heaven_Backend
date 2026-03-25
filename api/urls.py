from django.urls import path, include
from hotels.views import HotelViewSet, CategoryViewSet, ReviewViewSet, HotelImageViewSet
from bookings.views import CartViewSet, CartItemViewSet, BookingViewSet, HasBookedHotel,payment_success,payment_fail,payment_cancel,initiate_payment
from rest_framework_nested import routers

# MAIN ROUTER
router = routers.DefaultRouter()
router.register("hotels", HotelViewSet, basename="hotels")  # changed
router.register("categories", CategoryViewSet)
router.register("carts", CartViewSet, basename="carts")
router.register("bookings", BookingViewSet, basename="bookings")  # changed

# NESTED ROUTER (HOTEL → reviews, images)
hotel_router = routers.NestedDefaultRouter(router, "hotels", lookup="hotel")  # changed

hotel_router.register("reviews", ReviewViewSet, basename="hotel-review")  # changed
hotel_router.register("images", HotelImageViewSet, basename="hotel-images")  # changed

# NESTED ROUTER (CART → items)
cart_router = routers.NestedDefaultRouter(router, "carts", lookup="cart")
cart_router.register("items", CartItemViewSet, basename="cart-item")


urlpatterns = [
    path("", include(router.urls)),
    path("", include(hotel_router.urls)),
    path("", include(cart_router.urls)),
    # AUTH
    path("auth/", include("djoser.urls")),
    path("auth/", include("djoser.urls.jwt")),
    # PAYMENT
    path('api/v1/payment/initiate/', initiate_payment),
    path('api/v1/payment/success/', payment_success),
    path('api/v1/payment/fail/', payment_fail),
    path('api/v1/payment/cancel/', payment_cancel),
    # CHECK USER BOOKED HOTEL
    path("bookings/has-booked/<int:hotel_id>/", HasBookedHotel.as_view()),  # changed
]
