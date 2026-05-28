from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from products.models import Product
import uuid

class ProductAPITests(APITestCase):
    def setUp(self):
        self.valid_payload = {
            "name": "Kelas Belajar Python",
            "sku": "DCD01",
            "description": "This is a sample description of the product.",
            "shop": "Dicoding",
            "location": "Bandung",
            "price": 1500000,
            "discount": 0,
            "category": "Course",
            "stock": 1000,
            "is_available": True,
            "picture": "https://www.shutterstock.com/image-vector/sample-red-square-grunge-stamp-260nw-338250266.jpg"
        }
        self.product = Product.objects.create(**self.valid_payload)

    def test_create_product_success(self):
        response = self.client.post('/products/', {
            "name": "New Course",
            "sku": "NEW01",
            "description": "New description",
            "shop": "New Shop",
            "location": "Jakarta",
            "price": 500000,
            "discount": 10,
            "category": "Education",
            "stock": 50,
            "is_available": True,
            "picture": "http://example.com/pic.png"
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('id', response.data)
        self.assertEqual(response.data['name'], "New Course")
        self.assertIn('_links', response.data)
        
        # Test non-slash version works as well
        response_noslash = self.client.post('/products', {
            "name": "New Course 2",
            "sku": "NEW02",
            "description": "New description",
            "shop": "New Shop",
            "location": "Jakarta",
            "price": 500000,
            "discount": 10,
            "category": "Education",
            "stock": 50,
            "is_available": True,
            "picture": "http://example.com/pic.png"
        }, format='json')
        self.assertEqual(response_noslash.status_code, status.HTTP_201_CREATED)

    def test_create_product_invalid(self):
        invalid_payload = self.valid_payload.copy()
        invalid_payload.pop('name') # name is required
        response = self.client.post('/products/', invalid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_products(self):
        response = self.client.get('/products/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('products', response.data)
        self.assertEqual(len(response.data['products']), 1)
        self.assertEqual(response.data['products'][0]['name'], "Kelas Belajar Python")

    def test_list_products_empty(self):
        Product.objects.all().delete()
        response = self.client.get('/products/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('products', response.data)
        self.assertEqual(response.data['products'], [])

    def test_get_product_detail_success(self):
        response = self.client.get(f'/products/{self.product.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], "Kelas Belajar Python")
        self.assertIn('_links', response.data)

    def test_get_product_detail_not_found(self):
        response = self.client.get('/products/590f5c38-e7cf-45c9-8b0a-0937f7de6fa9/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data, {"detail": "Not found."})

        # Test invalid UUID format
        response_invalid_uuid = self.client.get('/products/invalid-uuid/')
        self.assertEqual(response_invalid_uuid.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response_invalid_uuid.data, {"detail": "Not found."})

    def test_update_product_success(self):
        updated_payload = self.valid_payload.copy()
        updated_payload['name'] = "Kelas Belajar Python Update"
        response = self.client.put(f'/products/{self.product.id}/', updated_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], "Kelas Belajar Python Update")

    def test_update_product_invalid(self):
        invalid_payload = self.valid_payload.copy()
        invalid_payload['price'] = "not-an-integer"
        response = self.client.put(f'/products/{self.product.id}/', invalid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_product_not_found(self):
        response = self.client.put('/products/590f5c38-e7cf-45c9-8b0a-0937f7de6fa9/', self.valid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data, {"detail": "Not found."})

    def test_delete_product_success(self):
        response = self.client.delete(f'/products/{self.product.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verify soft delete
        self.product.refresh_from_db()
        self.assertTrue(self.product.is_delete)
        self.assertFalse(self.product.is_available)

        # Still accessible via detail endpoint
        detail_response = self.client.get(f'/products/{self.product.id}/')
        self.assertEqual(detail_response.status_code, status.HTTP_200_OK)
        self.assertTrue(detail_response.data['is_delete'])

        # Not accessible via list endpoint
        list_response = self.client.get('/products/')
        self.assertEqual(len(list_response.data['products']), 0)

    def test_delete_product_not_found(self):
        response = self.client.delete('/products/590f5c38-e7cf-45c9-8b0a-0937f7de6fa9/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data, {"detail": "Not found."})

    def test_search_product_by_name(self):
        response = self.client.get('/products/?name=Python')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['products']), 1)
        self.assertEqual(response.data['products'][0]['name'], "Kelas Belajar Python")

        response_empty = self.client.get('/products/?name=NonExistent')
        self.assertEqual(response_empty.status_code, status.HTTP_200_OK)
        self.assertEqual(response_empty.data['products'], [])

    def test_search_product_by_location(self):
        response = self.client.get('/products/?location=Bandung')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['products']), 1)
        self.assertEqual(response.data['products'][0]['location'], "Bandung")
