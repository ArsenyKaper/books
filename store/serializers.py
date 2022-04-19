from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from store.models import Book, UserBookRelation


class BooksSerializer(ModelSerializer):
    likes_count = serializers.SerializerMethodField()
    anotated_likes = serializers.IntegerField(read_only=True)


    class Meta:
        model = Book
        fields = ['id', 'name', 'price', 'author_name', 'likes_count', 'anotated_likes']

    # инстанс это книг которую мы сериализуем в данный момент что приходит
    # book  это поле в UserBookRelation то есть конкретная книга
    def get_likes_count(self, instance):
        return UserBookRelation.objects.filter(book=instance, like=True).count()


class UserBookRelationSerializer(ModelSerializer):
    class Meta:
        model = UserBookRelation
        # не берем юзера потому что он в сесии отдельно и сам передает id сразу
        fields = ('book', 'like', 'in_bookmarks', 'rate')
