def factorial(n):
    """Возвращает n!"""
    return 1 if n < 2 else n * factorial(n - 1)

fruits = ['strawberry', 'fig', 'apple', 'cherry', 'raspberry', 'banana']
print(sorted(fruits, key=lambda word: word[::-1]))

# Девять вызываемых типов
# 1. Пользовательские функции
# 2. Встроенные функции
# 3. Встроенные методы
# 4. Методы
# 5. Классы
# 6. Экземпляры классов
# 7. Генераторные функции
# 8. Платформенные сопрограммы (async def)
# 9. Асинхронные генераторные функции

objcts = [abs, str, "Ni!"]
print([callable(obj) for obj in objcts])
#callable(obj) - узнать является ли объект вызываемым

# Пользовательские вызываемые типы
import random

class BingoCage:

    def __init__(self, items):
        self._items = list(items)
        random.shuffle(self._items)

    def pick(self):
        try:
            return self._items.pop()
        except IndexError:
            raise IndexError("pick from empty BingoCage")

    def __call__(self):
        # Позволяет писать просто bingo(), вместо bingo.pick()
        return self.pick()

bingo = BingoCage(range(3))
print(bingo.pick())
print(bingo())
print(bingo())
print(callable(bingo))

# Чисто именованные параметры
def tag(name, *concent, class_=None, **attrs):
    """Сгенерировать один или несколько HTML-тегов"""
    if class_ is not None:
        attrs["class"] = class_
    attr_pairs = (f' {attr}="{value}"' for attr, value in sorted(attrs.items()))
    attr_str = "".join(attr_pairs)
    if concent:
        elements = (f"<{name}{attr_str}>{c}</{name}>" for c in concent)
        return "\n".join(elements)
    else:
        return f"<{name}{attr_str} />"

print(tag("br"))
print(tag("p", "hello"))
print(tag("p", "hello", "world"))
print(tag("p", "hello", id=33))
print(tag("p", "hello", "world", class_="sidepar"))
my_tag = {"name": "img", "title": "Sunset Boulevar",
          "src": "sunset.jpg", "class": "framed"}
print(tag(**my_tag))

# Если вы вообще не хотите поддерживать позиционные аргументы, оставив возможность
# задавать чисто именованные, включите в сигнатуру * саму по себе.
def f(a, *, b):
    return a, b

# Чисто позиционные параметры
# Все аргументы слева от / будут чисто позиционными. Параметры после / будут работать как обычно.
def divmod(a, b, /):
    return (a // b, a % b)

# Модуль Operator
from functools import reduce

def factorial(n):
    return reduce(lambda a, b: a * b, range(1, n + 1))
print(factorial(5))

from operator import mul

def factorial(n):
    return reduce(mul, range(1, n + 1))
print(factorial(5))

from operator import itemgetter

metro_data = [('Tokyo', 'JP', 36.933, (35.689722, 139.691667)),
              ('Delhi NCR', 'IN', 21.935, (28.613889, 77.208889)),
              ('Mexico City', 'MX', 20.142, (19.433333, -99.133333)),]

cc_name = itemgetter(1, 0)
for city in metro_data:
    print(cc_name(city))

from functools import partial
triple = partial(mul, 3)
print(triple(7))

