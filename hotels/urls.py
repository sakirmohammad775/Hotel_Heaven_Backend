from django.urls import path
from hotels import views

urlpatterns = [
    path('', views.HotelList.as_view(), name='hotel-list'),
    path('<int:id>/', views.HotelDetails.as_view(), name='hotel-details'),
]