import json

from django.contrib.auth.models import User
from django.db.models import Count, Case, When
from django.urls import reverse
from rest_framework import status
from rest_framework.exceptions import ErrorDetail
from rest_framework.test import APITestCase

from store.models import Book, UserBookRelation
from store.serializers import BooksSerializer


class BooksApiTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create(username='test_username',)
        self.book1 = Book.objects.create(name='Test book 1', price=25,
                                          author_name='Author 1',
                                          owner=self.user)
        self.book2 = Book.objects.create(name='Test book 2', price=55,
                                          author_name='Author 5')
        self.book3 = Book.objects.create(name='Test book Author 1', price=55,
                                          author_name='Author 2')


    def test_get(self):
        url = reverse('book-list')
        response = self.client.get(url)
        books = Book.objects.all().annotate(
            anotated_likes=Count(Case(When(userbookrelation__like=True, then=1))))
        serializer_data = BooksSerializer(books, many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)



    def test_get_filter(self):
        url = reverse('book-list')
        response = self.client.get(url, data={'price': '55'})
        books = Book.objects.filter(id__in=[self.book2.id, self.book3.id]).annotate(
            anotated_likes=Count(Case(When(userbookrelation__like=True, then=1))))
        serializer_data = BooksSerializer(books, many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_get_search(self):
        url = reverse('book-list')
        books = Book.objects.filter(id__in=[self.book1.id, self.book3.id]).annotate(
            anotated_likes=Count(Case(When(userbookrelation__like=True, then=1))))
        response = self.client.get(url, data={'search': 'Author 1'})
        serializer_data = BooksSerializer(books, many=True).data
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
        self.assertEqual(self.user, Book.objects.last().owner)



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

    def test_update_not_owner(self):
        self.user2 = User.objects.create(username='test_username2', )
        url = reverse('book-detail', args=(self.book1.id,))
        data = {
            "name": self.book1.name,
            "price": 575,
            "author_name": self.book1.author_name
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user2)
        response = self.client.put(url, data=json_data,
                                   content_type='application/json')

        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)
        self.assertEqual({'detail': ErrorDetail(string='You do not have permission to perform this action.',
                                                code='permission_denied')}, response.data)
        self.book1.refresh_from_db()
        self.assertEqual(25, self.book1.price)

    def test_update_not_owner_but_staff(self):
        self.user2 = User.objects.create(username='test_username2',
                                         is_staff=True)
        url = reverse('book-detail', args=(self.book1.id,))
        data = {
            "name": self.book1.name,
            "price": 575,
            "author_name": self.book1.author_name
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user2)
        response = self.client.put(url, data=json_data,
                                   content_type='application/json')

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.book1.refresh_from_db()
        self.assertEqual(575, self.book1.price)




class BooksRelationTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create(username='test_username')
        self.user2 = User.objects.create(username='test_username_2')
        self.book1 = Book.objects.create(name='Book 1',
                                         price=25,
                                         author_name='Author 1',
                                         owner=self.user)
        self.book2 = Book.objects.create(name='Book 2',
                                         price=55,
                                         author_name='Author 5')

    def test_like(self):
        url = reverse('userbookrelation-detail', args=(self.book1.id,))

        data = {
            'like': True
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.patch(url, data=json_data,
                                     content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.book1.refresh_from_db()
        relation = UserBookRelation.objects.get(user=self.user,
                                                book=self.book1)
        self.assertTrue(relation.like)

        data = {
            'in_bookmarks': True
        }
        json_data = json.dumps(data)
        response = self.client.patch(url, data=json_data,
                                     content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        relation = UserBookRelation.objects.get(user=self.user,
                                                book=self.book1)
        self.assertTrue(relation.in_bookmarks)

    def test_rate(self):
        url = reverse('userbookrelation-detail', args=(self.book1.id,))

        data = {
            'rate': 3
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.patch(url, data=json_data,
                                     content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.book1.refresh_from_db()
        relation = UserBookRelation.objects.get(user=self.user,
                                                book=self.book1)
        self.assertEqual(3, relation.rate)

    def test_rate_wrong(self):
        url = reverse('userbookrelation-detail', args=(self.book1.id,))

        data = {
            "rate": 6,
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.patch(url, data=json_data,
                                     content_type='application/json')
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code, response.data)
