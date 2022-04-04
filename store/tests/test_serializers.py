from unittest import TestCase

from store.models import Book
from store.serializers import BooksSerializer


class BooksSerializerTestCase(TestCase):
    def test_ok(self):
        book1 = Book.objects.create(name='Book 1', price=25)
        book2 = Book.objects.create(name='Test Book 2', price=55)
        data = BooksSerializer([book1, book2], many=True).data
        expeted_data = [
            {
                'id': book1.id,
                'name': 'Book 1',
                'price': '25.00'
            },
            {
                'id': book2.id,
                'name': 'Test Book 2',
                'price': '55.00'
            },
        ]
        self.assertEqual(expeted_data, data)
