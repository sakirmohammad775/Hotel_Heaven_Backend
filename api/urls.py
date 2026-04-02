from django.urls import path, include
from hotels.views import HotelViewSet, CategoryViewSet, ReviewViewSet, HotelImageViewSet,ConciergeBotView
from bookings.views import CartViewSet, CartItemViewSet, BookingViewSet, HasBookedHotel, payment_success, payment_fail, payment_cancel, initiate_payment
from rest_framework_nested import routers

# MAIN ROUTER
router = routers.DefaultRouter()
router.register("hotels", HotelViewSet, basename="hotels")
router.register("categories", CategoryViewSet)
router.register("carts", CartViewSet, basename="carts")
router.register("bookings", BookingViewSet, basename="bookings")

# NESTED ROUTER (HOTEL → reviews, images)
hotel_router = routers.NestedDefaultRouter(router, "hotels", lookup="hotel")
hotel_router.register("reviews", ReviewViewSet, basename="hotel-review")
hotel_router.register("images", HotelImageViewSet, basename="hotel-images")

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
    # PAYMENT ✅ no api/v1/ prefix here — it's already added by main urls.py
    path('payment/initiate/', initiate_payment),
    path('payment/success/', payment_success),
    path('payment/fail/', payment_fail),
    path('payment/cancel/', payment_cancel),
    # CHECK USER BOOKED HOTEL
    path("bookings/has-booked/<int:hotel_id>/", HasBookedHotel.as_view()),
    
    
    # 🔹 Add this line exactly here
    path("concierge/", ConciergeBotView.as_view(), name="concierge-bot"),
    
]