'''
Хотите понять, что делает тип в Python, - узнайте, какие методы он предоставляет.

Есть 4 способа способа определения и использования интерфейсов:
> Утиная типизация
> Гусиная типизация
> Статическая типизация
> Статическая утиная тпиизация
'''

# Два вида протоколов
class Vowels:
    def __getitem__(self, i):
        return 'AEIOU'[i]

'''
Реализации метода __getitem__ достаточно для получения элементов по индексу, а также поддержки итерирования и оператора in.
Специальный метод __getitem__ - ключ к протоколу последовательности.
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

# Партизанское латание как средство реализации протокола во время выполнения
from random import shuffle

deck = FrenchDeck()

def set_card(deck, position, card):
    deck._cards[position] = card

FrenchDeck.__setitem__ = set_card
shuffle(deck)
print(deck[:5])

# Защитное программирование и принцип быстрого отказа
'''
Защитное программирование - набор практических навыков, повышающих безопасность при столкновении с беспечными программистами.

Многие ошибки можно отловить только во время выполнения, даже в статически типизированных языках.
В динамически типизированном языке принцип быстрого отказа - прекрасный совет по созданию более безопасных и удобных
для сопровождения программ. Быстрый отказ означает, что нужно возбудить исключение как можно раньше, например
отвергать недопустимые аргументы в самом начале тела функции.
'''

# Гусиная типизация
'''
Гусиная типизация - это подход к проверке типов во время выполнения, основанный на применении ABC.
'''

# Создание подкласса ABC

from collections import abc
from dataclasses import dataclass

@dataclass
class Card:
    rank: str
    suit: str

class FrenchDeck2(abc.MutableSequence):
    ranks = [str(rank) for rank in range(2, 11)] + list('JQKA')
    suits = 'spades diamonds clubs hearts'.split()

    def __init__(self):
        self._cards = [Card(rank, suit) for suit in self.suits
                                        for rank in self.ranks]

    def __len__(self):
        return len(self._cards)

    def __getitem__(self, position):
        return self._cards[position]

    def __setitem__(self, position, value):
        '''Метод __setitem__ - всё, что нам нужно для поддержки тасования'''
        self._cards[position] = value

    def __delitem__(self, position):
        '''Чтобы создать подкласс MutableSequence, нам придется реализловать также метод __delitem__'''
        del self._cards[position]

    def insert(self, position, value):
        '''Также необходимо реализовать метод insert. Третий абстрактный метод abc.MutableSequence'''
        self._cards.insert(position, value)

# ABC в стандартной библиотеке
'''
Группы классов:
> Iterable, Container, Sized:
Любая коллекция должна быть наследована этим ABC, либо реализовывать совместимые протоколы.
Класс Iterable поддерживает итерирование методом __iter__;
Container поддерживает оператор in методом __contains__;
Sized поддерживает функцию len() методом __len__.

> Collection:
У этого ABC нет собственных методов, но он был добавлен, чтобы было проще создавать подклассы,
наследующие Iterable, Container и Sized.

> Sequence, Mapping, Set:
Это основные типы неизменяемых коллекций, и у каждого есть изменяемый подкласс.

> MappingView:
Объекты, возвращенные методами отображения .items(), .keys() и .values(), 
наследуют классам ItemView, KeysView и ValuesView соотвественно.
Первые два наследуют интерфейс класса Set.

> Iterator:
Является подклассом Iterable.

> Callable, Hashable:
Их основное назначение - поддержка проверки типов объектов, которые должны быть вызываемыми или хешируемыми.
'''

# Определение и использование ABC

import abc

class Tombola(abc.ABC): # Чтобы определить ABC создаем подкласс abc.ABC

    @abc.abstractmethod
    def load(self, iterable):
        '''Добавить элементы из итерируемого объекта'''

    @abc.abstractmethod
    def pick(self):
        '''Удалить случайный элемент и вернуть его.

        Этот метод должен возбуждать исключение 'LookupError', если объект пуст.
        '''

    def loaded(self):
        '''Вернуть `True`, если есть хотя бы 1 элемент, иначе `False`.

        Конкретные методы ABC должны зависеть только от открытого интерфейса данного ABC
        (т.е. от других его конкретных или абстрактных методов или свойств)
        '''
        return bool(self.inspect())

    def inspect(self):
        '''Вернуть отсортированный кортеж, содержащий оставшиеся в данный момент элементы.'''
        items = []
        while True:
            try:
                items.append(self.pick())
            except LookupError:
                break
        self.load(items)
        return tuple(items)

# Синтаксические детали ABC
'''
Лучший способ объявить ABC - сделать его подклассом abc.ABC или какого-нибудь другого ABC.
'''

# Создание подклассов ABC

import random

class BingoCage(Tombola):

    def __init__(self, items):
        self._randomizer = random.SystemRandom()
        self._items = []
        self.load(items)

    def load(self, items):
        self._items.extend(items)
        self._randomizer.shuffle(self._items)

    def pick(self):
        try:
            return self._items.pop()
        except IndexError:
            raise LookupError('pick from empty BingoCage')

    def __call__(self):
        return self.pick()

class LottoBlower(Tombola):

    def __init__(self, iterable):
        self._balls = list(iterable)

    def load(self, iterable):
        self._balls.extend(iterable)

    def pick(self):
        try:
            position = random.randrange(len(self._balls))
        except ValueError:
            raise LookupError(f'pick from empty {type(self).__name__}')
        return self._balls.pop(position)

    def loaded(self):
        return bool(self._balls)

    def inspect(self):
        return tuple(self._balls)

# Виртуальный подкласс Tombola
'''
Важнейшая характеристика гусиной типизации - возможность регистрировать класс как виртуальный подкласс ABC, даже без наследования.
При этом мы обещаем, что класс честно реализует интерфейс, определенный в ABC, а Python верит нам на слово, не производя проверку.
Если мы соврем, то будем наказаны исключением во время исполнения.

Это делается путем вызова метода register абстрактного базового класса.
В результате зарегистрированный класс становится виртуальным подклассом ABC и распознается в качестве такового 
функцией issubclass, однако не наследует ни методы, ни атрибуты ABC.
'''

@Tombola.register # TomboList зарегистрирован как виртуальный подкласс Tombola
class TomboList(list): # Расширяет list

    def pick(self):
        if self:
            position = random.randrange(len(self))
            return self.pop(position)
        else:
            raise LookupError('pop from empty TomboList')

    load = list.extend # TomboList.load тоже самое, что и list.extend

    def loaded(self):
        return bool(self)

    def inspect(self):
        return tuple(self)

#Tombola.register(TomboList) - альтернатива декоратора @Tombola.register
print(issubclass(TomboList, Tombola))

# Статические протоколы
# Типизированная функция double

from typing import Protocol, TypeVar

T = TypeVar('T')

class Repeatable(Protocol):

    def __mul__(self: T, repeat_count: int) -> T:
        pass

RT = TypeVar('RT', bound=Repeatable)

def double(x: RT) -> RT:
    return x * 2
