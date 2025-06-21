from django.urls import path
from .views import ProductListAPIView, yookassa_confirm

urlpatterns = [
    path('products/', ProductListAPIView.as_view(), name='product-list'),
    path("payment/confirm/", yookassa_confirm, name="yookassa_confirm")
]
