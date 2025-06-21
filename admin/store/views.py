import json
from django.http import HttpResponse
from rest_framework import generics
from .models import Product, Order
from .serializers import ProductSerializer
from django.views.decorators.csrf import csrf_exempt


class ProductListAPIView(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


@csrf_exempt
def yookassa_confirm(request):
    body = json.loads(request.body)
    if body.get("object", {}).get("status") == "succeeded":
        order_id = body["object"]["metadata"]["order_id"]
        order = Order.objects.get(id=order_id)
        order.paid = True
        order.save()
    return HttpResponse(status=200)