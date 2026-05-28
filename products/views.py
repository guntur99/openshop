from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ParseError
from .models import Product
from .serializers import ProductSerializer

class ProductListCreateAPIView(APIView):
    def get(self, request):
        queryset = Product.objects.filter(is_delete=False)
        name_query = request.query_params.get('name')
        location_query = request.query_params.get('location')

        if name_query:
            queryset = queryset.filter(name__icontains=name_query)
        if location_query:
            queryset = queryset.filter(location__icontains=location_query)

        serializer = ProductSerializer(queryset, many=True, context={'request': request})
        return Response({"products": serializer.data}, status=status.HTTP_200_OK)

    def post(self, request):
        try:
            data = request.data
        except ParseError as e:
            try:
                content_length = int(request.META.get('CONTENT_LENGTH', 0))
            except (ValueError, TypeError):
                content_length = 0
            if content_length == 0:
                data = {}
            else:
                raise e
        serializer = ProductSerializer(data=data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductDetailAPIView(APIView):
    def get_object(self, pk):
        try:
            return Product.objects.get(pk=pk)
        except (Product.DoesNotExist, ValueError):
            return None

    def get(self, request, pk):
        product = self.get_object(pk)
        if product is None:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = ProductSerializer(product, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        product = self.get_object(pk)
        if product is None:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        try:
            data = request.data
        except ParseError as e:
            try:
                content_length = int(request.META.get('CONTENT_LENGTH', 0))
            except (ValueError, TypeError):
                content_length = 0
            if content_length == 0:
                data = {}
            else:
                raise e

        serializer = ProductSerializer(product, data=data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        product = self.get_object(pk)
        if product is None:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        product.is_delete = True
        product.is_available = False
        product.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
