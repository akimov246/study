# Представления объекта
'''
repr() - Вернуть строку, представляющую объект в виде, удобном для разработчика.
Это то, что мы видим, когда объект отображается на консоли Python или в отладчике.

str() - Вернуть строку, представляющую объект в виде, удобном для пользователя.
Это то что печатает функция print().

bytes() - Получить представление объекта в виде последовательности байтов.

format() - Вызывается f-строками, встроенной функцией format() и методом str.format() для получения
строкового представления объектов с помощью специальных форматных кодов.
'''

from array import array
import math

# Класс вектора
class Vector2d:
    typecode = 'd' # Аттрибут класса, которым мы воспользуемся, когда будем преобразовывать экземпляры Vector2d в последовательность байтов и наоборот.

    def __init__(self, x, y):
        self.__x = float(x)
        self.__y = float(y)

    @property
    def x(self):
        return self.__x

    @property
    def y(self):
        return self.__y

    def __iter__(self):
        '''Наличие метода __iter__ делает Vector2d итерируемым;
           Именно благодаря ему работает распаковка (например, x, y = my_vector).
        '''
        return (i for i in (self.x, self.y))

    def __repr__(self):
        class_name = type(self).__name__
        return '{}({!r}, {!r})'.format(class_name, *self)
        #return f'{class_name}{self.x, self.y}'

    def __str__(self):
        '''Из итерируемого объекта легко построить кортеж для отображения в виде упорядоченной пары'''
        return str(tuple(self))

    def __bytes__(self):
        return (bytes([ord(self.typecode)]) +
                bytes(array(self.typecode, self)))

    def __eq__(self, other):
        return tuple(self) == tuple(other)

    def __abs__(self):
        return math.hypot(self.x, self.y)

    def __bool__(self):
        return bool(abs(self))

    @classmethod
    def frombytes(cls, octets):
        typecode = chr(octets[0])
        memv = memoryview(octets[1:]).cast(typecode)
        return cls(*memv)

    def __format__(self, format_spec=''):
        if format_spec.endswith('p'):
            format_spec = format_spec[:-1]
            coords = (abs(self), self.angle())
            outer_fmt = '<{}, {}>'
        else:
            coords = self
            outer_fmt = '({}, {})'
        components = (format(c, format_spec) for c in coords)
        return outer_fmt.format(*components)

    def angle(self):
        return math.atan2(self.y, self.x)

    def __hash__(self):
        '''Рекомендуется вычислять hash кортежа покомпонентно'''
        return hash((self.x, self.y))


v = Vector2d(1, -2)
print(hash(v))
print(complex(v))

# Декораторы classmethod и staticmethod
'''
Декоратор classmethod изменяет способ вызова метода таким образом, что в качестве первого аргумента передается сам класс, а не экземпляр.

Декоратор staticmethod изменяет метод так, что он не получает в первом аргументе ничего специального.
По существу, статический метод - это просто обычная функция, определенная в теле класса, а не на уровне модуля.
'''

# Сравнение декораторов classmethod и staticmethod
class Demo:
    @classmethod
    def klassmeth(*args):
        return args
    @staticmethod
    def statmeth(*args):
        return args

print(Demo.klassmeth('spam'))
print(Demo.statmeth('spam'))

# Форматирование при выводе
brl = 1 / 4.82
print(brl)
print(format(brl, '0.4f'))
print('1 BRL = {rate:0.2f}'.format(rate=brl))
print(f'1 USD = {1 / brl:0.2f} BRL')
