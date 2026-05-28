from django.urls import path
from products.views import ProductListCreateAPIView, ProductDetailAPIView
from django.views.generic import RedirectView


urlpatterns = [
    path('', RedirectView.as_view(url='products/', permanent=False), name='root-redirect'),
    path('products/', ProductListCreateAPIView.as_view(), name='product-list-create'),
    path('products/<uuid:pk>/', ProductDetailAPIView.as_view(), name='product-detail'),
]