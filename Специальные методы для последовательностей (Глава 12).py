# Vector: пользовательский тип последовательности

# Vector, попытка №1: совместимость с Vector2d
import operator

from array import array
import reprlib
import math

class Vector:

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
        return tuple(self) == tuple(other)

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




# Протоколы и утиная типизация
'''
В ООП протоколом называется неформальный интерфейс, определенный только в документации, но не в коде.
Например, протокол последовательности в Python подразумевает только наличие методов __len__ и __getitem__.
'''
from dataclasses import dataclass

@dataclass
class Card:
    rank: str
    suit: str

class FrenchDeck:

    ranks = [str(n) for n in range(2, 11)] + list('JQKA')
    suits = 'spades diamonds clubs hearts'.split()

    def __init__(self):
        self._cards = [Card(rank, suit) for suit in self.suits
                                        for rank in self.ranks]

    def __len__(self):
        return len(self._cards)

    def __getitem__(self, position):
        return self._cards[position]

'''
В классе frenchDeck применяются разнообразные средства Python, потому что он реализует протокол последовательности, 
хотя нигде в коде об этом явно не сказано.
Мы говорим, что он является последовательностью, потому что ведет себя как последовательность, а только это и важно.
Такой подход получил название "утиная типизация".
'''

v = Vector(range(5))
print(v[1:5:3])
