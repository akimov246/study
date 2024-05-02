# Основы перегрузки операторов
# Унарные операторы
'''
> Унарный арифметический минус. Если х равно -2, то -х == 2. (реализуется с помощью __neg__)

> Унарный арифметический плюс. Обычно x == +x, но есть несколько особых случаев, когда это неверно. (реализуется с помощью __pos__)

> Поразрядная инверсия целого числа, определяется как ~x == -(x + 1). Если x равно 2, то ~x == -3. (реализуется с помощью __invert__)

> Модуль числа. abs(-x) == x. (реализуется с помощью __abs__)

Поддержать унарные операторы легко. Достаточно реализовать соответстующий специальный метод, который принимает единственный
аргумент self. Логика этого метода может быть произвольной, но должно удовлетворяться фундаментальное правило:
оператор всегда возвращает новый объект. Иначе говоря, не модифицируйте self, а создавайте и возвращайте новый экземпляр
подходящего типа.
'''

# Класс Vector из Главы 12

import itertools
import operator
import functools
from array import array
import reprlib
import math
from collections import abc

class Vector:

    __match_args__ = ('x', 'y', 'z', 't')

    typecode = 'd'

    def __init__(self, components):
        self._components = array(self.typecode, components)

    def __iter__(self):
        return iter(self._components)

    def __repr__(self):
        components = reprlib.repr(self._components)
        components = components[components.find('['):-1]
        return f'Vector({components})'

    def __str__(self):
        return str(tuple(self))

    def __bytes__(self):
        return (bytes([ord(self.typecode)]) +
                bytes(self._components))

    def __eq__(self, other):
        # Простая реализация
        #return tuple(self) == tuple(other)

        # Реализация лучше. Работает быстрее и постребляет меньше памяти (по крайней мере для больших векторов)
        #return len(self) == len(other) and all(a == b for a, b in zip(self, other))
        if len(self) != len(other):
            return False
        for a, b in zip(self, other):
            if a != b:
                return False
        return True

    def __abs__(self):
        return math.hypot(*self)

    def __bool__(self):
        return bool(abs(self))

    @classmethod
    def frombytes(cls, octets):
        typecode = chr(octets[0])
        memv = memoryview(octets[1:]).cast(typecode)
        return cls(memv)

    # Vector, попытка №2: последовательность, допускающая срез
    def __len__(self):
        return len(self._components)

    def __getitem__(self, key):
        '''Чтобы срезы возвращали нам экземпляр нашего класса'''
        if isinstance(key, slice):
            cls = type(self)
            return cls(self._components[key])
        '''Функция operator.index() вызывает специальный метод __index__.
            Основное различие между operator.index() и int() заключается в том, 
            что первый предназначен для этой конкретной цели.
            Например, int(3.14) вернет 3, а operator.index(3.14) возбуждает исключение TypeError, 
            потому что float не может использоваться в качестве индекса.'''
        index = operator.index(key)
        return self._components[index]

    # Vector, попытка №3: доступ к динамическим атрибутам
    '''
    Иногда удобно обращаться к нескольким первым компонентам по именам, состоящим из одной буквы,
    например x, y, z, вместо v[0], v[1], v[2].
    В классе Vector2d мы предоставляли доступ для чтения компонентам x и y с помощью декоратора @property.
    Мы могли бы зависти в Vector четыре свойства, но это утомительно. Специальный метод __getattr__ позволяет
    сделать это по-другому и лучше.
    Метод __getattr__ вызывается интерпретатором, если поиск атрибута завершается неудачно.
    Иначе говоря, анализируя выражение my_obj.x, Python проверяет, если у объекта my_obj атрибут с именем x;
    если нет, поиск повторяется в классе (my_obj.__class__), а затем ввверх по иерархии наследования. 
    Если атрибут x всё равно не найден, то вызывается метод __getattr__, пределенный в классе my_obj, причем
    ему передаетя self и имя атрибута в виде строки (например 'x').
    '''

    def __getattr__(self, name):
        cls = type(self)
        try:
            pos = cls.__match_args__.index(name)
        except ValueError:
            pos = -1
        if 0 <= pos < len(cls.__match_args__):
            return self._components[pos]
        msg = f'{cls.__name__!r} object has no attribute {name!r}'
        raise AttributeError(msg)

    def __setattr__(self, name, value):
        '''В классе Vector мы хотим возбуждать исключение AttributeError при любой попытке
        присвоить значение атрибуту, имя которого состоит из одной строчной буквы'''
        cls = type(self)
        if len(name) == 1:
            if name in cls.__match_args__:
                error = f'readonly attribute {name!r}'
            elif name.islower():
                error = f"can't set attributes 'a' to 'z' in {cls.__name__!r}"
            else:
                error = ''
            if error:
                raise AttributeError(error)
        super().__setattr__(name, value) # функция super() - быстрый способ обратиться к методам суперкласса.

    # Vector, попытка №4: хеширование и ускорение оператора ==
    def __hash__(self):
        #hashes = map(hash, self._components)
        hashes = (hash(x) for x in self._components)
        '''При использовании reduce рекомендуется задавать третий аргумент,
        reduce(function, iterable, initializer), чтобы предотвратить появления исключения.
        Значение initializer возвращается, если последовательность пуста, а кроме того, 
        используется в качестве первого аргумента в цикле редукции, поэтому оно должно быть
        нейтральным элементом относительно выполняемой операции.
        Так для операций: +, |, ^ initializer должен быть равен 0, а для *, & 1 (единице)'''
        return functools.reduce(operator.xor, hashes, 0)

    # Vector, попытка №5: форматирование
    def angle(self, n):
        r = math.hypot(*self[n:])
        a = math.atan2(r, self[n - 1])
        if (n == len(self) - 1) and (self[-1] < 0):
            return math.pi * 2 - a
        else:
            return a

    def angles(self):
        return (self.angle(n) for n in range(1, len(self)))

    def __format__(self, format_spec=''):
        if format_spec.endswith('h'): # Гиперсферические координаты
            format_spec = format_spec[:-1]
            # itertools.chain порождает генератор который перебирает элементы всех iterables
            coords = itertools.chain([abs(self)], self.angles())
            outer_format = '<{}>'
        else:
            coords = self
            outer_format = '({})'
        components = (format(c, format_spec) for c in coords)
        return outer_format.format(', '.join(components))

    # Еще несколько дополнительных операторов: унарные - и + (Глава 16)
    def __neg__(self):
        return Vector(-x for x in self)

    def __pos__(self):
        return -Vector(self)

    # Перегрузка операторов сложения векторов +
    def __add__(self, other):
        try:
            pairs = itertools.zip_longest(self, other, fillvalue=0.0)
            return Vector(a + b for a, b in pairs)
        except TypeError:
            return NotImplemented

    def __radd__(self, other):
        return self + other
    # Или __radd__ = __add__

    # Перегрузка оператора умножения на скаляр *
    def __mul__(self, scalar):
        try:
            factor = float(scalar)
        except TypeError:
            return NotImplemented
        return Vector(n * factor for n in self)

    def __rmul__(self, scalar):
        return self * scalar

    # Использование @ как инфиксного оператора
    def __matmul__(self, other):
        if (isinstance(other, abc.Sized) and
            isinstance(other, abc.Iterable)):
            if len(self) == len(other):
                return sum(a * b for a, b in zip(self, other))
            else:
                raise ValueError('@ requiers vectors of equal length.')
            # другой вариант
            # try:
            #     return sum(a * b for a, b in zip(self, other, strict=True))
            # except ValueError:
            #     raise ValueError('@ requiers vectors of equal length.')
        else:
            return NotImplemented

    def __rmatmul__(self, other):
        return self @ other






