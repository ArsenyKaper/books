# def operations(a, b, c):
#     if c == '+':
#         return a + b
#     if c == '-':
#         return a - b
#     if c == '*':
#         return a * b
from django.db.models import Avg

from store.models import UserBookRelation


# aggregate() - агрегация напрямую без аннотации
# book - тот объект (книга) что будет приходит
# rating - любая перменная
def set_rating(book):
    # обращаемся непосредственн к связям (не через Book, а сразу к UserBookRelation)

    rating = UserBookRelation.objects.filter(book=book).aggregate(rating=Avg('rate')).get('rating')
    book.rating=rating#книга.поле рейтинга, в него записываем тот рейтинг что получили
    book.save()

    # в представлении было: rating=Avg('userbookrelation__rate')
    # мы через книгу в СВЯЗИ агрегuировали поле rate

    # aggregate(rating=Avg('rate')) - создаст словарь {rating:значение(Avg('rate'))}
    #get даст нам не словарь, а само значение