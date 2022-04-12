import json

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from store.models import Book
from store.serializers import BooksSerializer


class BooksApiTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create(username='test_username')

        self.book1 = Book.objects.create(name='Book 1',
                                         price=25,
                                         author_name='Author 1')
        self.book2 = Book.objects.create(name='Book 2',
                                         price=55,
                                         author_name='Author 5')
        self.book3 = Book.objects.create(name='Book 3 Author 1',
                                         price=25,
                                         author_name='Author 2')

    def test_get(self):
        url = reverse('book-list')
        response = self.client.get(url)
        serializer_data = BooksSerializer([self.book1, self.book2, self.book3], many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_create(self):
        url = reverse('book-list')
        self.assertEqual(3, Book.objects.all().count())

        data = {
            'name': 'Programig in Python 3',
            'price': '250.00',
            'author_name': 'Mark Summmerfield'
        }

        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.post(url,
                                    data=json_data,
                                    content_type='application/json')

        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(4, Book.objects.all().count())

    def test_update(self):
        url = reverse('book-detail', args=(self.book1.id,))
        data = {
            'name': self.book1.name,
            'price': 575,
            'author_name': self.book1.author_name
        }

        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.put(url,
                                   data=json_data,
                                   content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.book1.refresh_from_db()
        self.assertEqual(575, self.book1.price)

    def test_get_filter(self):
        url = reverse('book-list')
        response = self.client.get(url, data={'search': 'Author 1'})
        serializer_data = BooksSerializer([self.book1, self.book3], many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_get_sort_by_price(self):
        url = reverse('book-list')
        response = self.client.get(url, data={'ordering': 'price'})
        serializer_data = BooksSerializer([self.book1, self.book3, self.book2], many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)
