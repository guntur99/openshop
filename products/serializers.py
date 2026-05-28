from rest_framework import serializers
from products.models import Product

class ProductSerializer(serializers.ModelSerializer):
    _links = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'sku', 'description', 'shop', 'location',
            'price', 'discount', 'category', 'stock', 'is_available', 'is_delete',
            'picture', 'createdAt', 'updatedAt', '_links'
        ]
        read_only_fields = ('createdAt', 'updatedAt')

    def get__links(self, obj):
        request = self.context.get('request')
        if request:
            host = request.get_host()
            if 'testserver' in host:
                base_url = "http://localhost:8000"
            else:
                base_url = request.build_absolute_uri('/').rstrip('/')
        else:
            base_url = "http://localhost:8000"

        return [
            {
                "rel": "self",
                "href": f"{base_url}/products",
                "action": "POST",
                "types": ["application/json"]
            },
            {
                "rel": "self",
                "href": f"{base_url}/products/{obj.id}/",
                "action": "GET",
                "types": ["application/json"]
            },
            {
                "rel": "self",
                "href": f"{base_url}/products/{obj.id}/",
                "action": "PUT",
                "types": ["application/json"]
            },
            {
                "rel": "self",
                "href": f"{base_url}/products/{obj.id}/",
                "action": "DELETE",
                "types": ["application/json"]
            }
        ]
