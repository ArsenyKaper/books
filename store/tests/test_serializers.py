from django.contrib.auth.models import User
from django.db.models import Count,Case,When
from django.test import TestCase

from store.models import Book, UserBookRelation
from store.serializers import BooksSerializer


class BookSerializerTestCase(TestCase):


    def test_ok(self):
        user_1 = User.objects.create(username='user_1')
        user_2 = User.objects.create(username='user_2')
        user_3 = User.objects.create(username='user_3')

        book_1 = Book.objects.create(name='Test book 1', price=25, author_name='Author 1', )
        book_2 = Book.objects.create(name='Test book 2', price=55, author_name='Author 2')

        UserBookRelation.objects.create(user=user_1,book=book_1,like=True)
        UserBookRelation.objects.create(user=user_2, book=book_1, like=True)
        UserBookRelation.objects.create(user=user_3, book=book_1, like=True)

        UserBookRelation.objects.create(user=user_1,book=book_2,like=True)
        UserBookRelation.objects.create(user=user_2, book=book_2, like=True)
        UserBookRelation.objects.create(user=user_3, book=book_2, like=False)

        books = Book.objects.all().annotate(
            anotated_likes=Count(Case(When(userbookrelation__like=True,then=1)))).order_by('id')
        # data = BooksSerializer([book_1, book_2], many=True).data
        data = BooksSerializer(books, many=True).data

        expected_data = [
            {
                'id': book_1.id,
                'name': 'Test book 1',
                'price': '25.00',
                'author_name': 'Author 1',
                'likes_count': 3,
                'anotated_likes': 3,
            },
            {
                'id': book_2.id,
                'name': 'Test book 2',
                'price': '55.00',
                'author_name': 'Author 2',
                'likes_count': 2,
                'anotated_likes': 2,
            },
        ]
        print(expected_data, data)
        self.assertEqual(expected_data, data)
