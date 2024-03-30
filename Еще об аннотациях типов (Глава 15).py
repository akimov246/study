# Перегруженные сигнатуры
'''
Функции в Python могут принимать различные комбинации аргументов.
Декоратор @typing.overload позволяет аннотировать эти комбинации. Это особенно важно, когда тип возвращаемого
функцией значения зависит от типа двух или более параметров.
'''
import functools
import operator
from collections.abc import Iterator
from typing import overload, Union, TypeVar

T = TypeVar('T')
S = TypeVar('S')

@overload
def sum(it: Iterator[T]) -> Union[T, int]: ...
@overload
def sum(it: Iterator[T], /, start: S) -> Union[T, S]: ...
def sum(it, /, start = 0):
    return functools.reduce(operator.add, it, start)

# Перегрузка max
from collections.abc import Callable, Iterable
from typing import Protocol, Any, TypeVar, overload, Union

class SupportsLessThan(Protocol):
    def __lt__(self, other: Any) -> bool: ...

T = TypeVar('T')
LT = TypeVar('LT', bound=SupportsLessThan)
DT = TypeVar('DT')

MISSING = object()
EMPTY_MSG = 'max() arg is an empty sequence'

@overload
def max(arg1: LT, arg2: LT, /, *args: LT, key: None = ...) -> LT: ...

@overload
def max(arg1: LT, arg2: LT, /, *args: T, key: Callable[[T], LT]) -> T: ...

@overload
def max(iterable: Iterable[LT], /, *, key: None = ...) -> LT: ...

@overload
def max(iterable: Iterable[T], /, *, key: Callable[[T], LT]) -> T: ...

@overload
def max(iterable: Iterable[LT], /, *, key: None = ..., default: DT) -> Union[LT, DT]: ...

@overload
def max(iterable: Iterable[T], /, *, key: Callable[[T], LT], default: DT) -> Union[T, DT]: ...

def max(first, *args, key=None, default=MISSING):
    if args:
        series = args
        candidate = first
    else:
        series = iter(first)
        try:
            candidate = next(series)
        except StopIteration:
            if default is not MISSING:
                return default
            raise ValueError(EMPTY_MSG) from None
    if key is None:
        for current in series:
            if candidate < current:
                candidate = current
    else:
        candidate_key = key(candidate)
        for current in series:
            current_key = key(current)
            if candidate_key < current_key:
                candidate = current
                candidate_key = current_key
    return candidate

# TypedDict

from typing import TypedDict

class BookDict(TypedDict):
    isbn: str
    title: str
    authors: list[str]
    pagecount: int

pp = BookDict(title='Programming Pearls',
              authors='Jon Bentley',
              isbn='0201657880',
              pagecount=256)
print(pp)
print(type(pp))
print(pp['title'])
print(BookDict.__annotations__)

# Приведение типов
'''
Приведения используются, чтобы подавить спонтанные предупреждения средства проверки типов и немного помочь ему,
когда оно не совсем понимает, что происходит.
'''
from typing import cast

def find_first_str(a: list[object]) -> str:
    index = next(i for i, x in enumerate(a) if isinstance(x, str))
    return cast(str, a[index])

print(find_first_str([123, 123, 123, '246']))

# Реализация обобщенного класса

import random
import abc

from collections.abc import Iterator
from typing import TypeVar, Generic

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

T = TypeVar('T')

class LottoBlower(Tombola, Generic[T]):
    '''В объявлениях обобщенных классов часто используется множественное наследование,
        поскольку мы должны унаследовать Generic, чтобы объявить формальные параметры-типы - в данном стучае Т'''

    def __init__(self, items: Iterable[T]) -> None:
        '''Аргумент items метода __init__ имеет тип Iterable[T], который превращается в Iterable[int],
        когда экземпляр объявляется как LottoBlower[int]'''
        self._balls = list[T](items)

    def load(self, items: Iterable[T]) -> None:
        self._balls.extend(items)

    def pick(self) -> T:
        '''Типом возвращаемого значения T в LottoBlower[int] становится int'''
        try:
            position = random.randrange(len(self._balls))
        except ValueError:
            raise LookupError('pick from empty LottoBlower')
        return self._balls.pop(position)

    def loaded(self) -> bool:
        return bool(self._balls)

    def inspect(self) -> tuple[T, ...]:
        return tuple(self._balls)

machine = LottoBlower[int](range(1, 11))

# Основы терминологии, относящейся к обобщенным типам
'''
> Обобщенный тип - тип, в объявлении которого присутствует одна или несколько перменных-типов.
Примеры: LottoBlower[T], abc.Mapping[KT, VT].

> Формальный параметр-тип - переменные-типы, встречающиеся в объявлении типа.
Пример: KT и VT в предудыщем примере abc.Mapping[KT, VT]

> Параметризованный тип - тип, объявленный с фактическими параметрами-типами.
Примеры: LottoBlower[int], abc.Mapping[str, float].

> Фактический параметр-тип - фактические типы, заданные в качестве параметров в объявлении параметризованного типа.
Пример: int в объявлении LottoBlower[int].
'''

# Вариантность
# Инвариантный разливочный аппарат

class Beverage:
    '''Любой напиток'''

class Juice(Beverage):
    '''Любой фруктовы сок'''

class OrangeJuice(Juice):
    '''Апельсиновый сок'''

T = TypeVar('T')

class BeverageDispenser(Generic[T]):
    '''Автомат, параметризованный типом напитка'''
    def __init__(self, beverage: T) -> None:
        self.beverage = beverage

    def dispense(self) -> T:
        return self.beverage

def install(dispenser: BeverageDispenser[Juice]) -> None:
    '''Установить автомат для разлива фруктовых соков'''

'''Говорят, что тип BeverageDispenser(Generic[T]) ивариантен, если BeverageDispenser[OrangeJuice] не совместим с
BeverageDispenser[Juice], не смотря на то, что OrangeJuice является подтипом Juice'''

juice_dispenser = BeverageDispenser(Juice())
install(juice_dispenser)

# Ковариантный разливочный автомат
'''Если мы хотим большей гибкости, т.е. нужно моделировать разливочные автоматы как обобщенный класс, 
который принимает тип напитка и его подтипы, то нужно сделать этот класс ковариантным'''

T_co = TypeVar('T_co', covariant=True)

class BeverageDispenser(Generic[T_co]):

    def __init__(self, beverage: T_co) -> None:
        self.beverage = beverage

    def dispense(self) -> T_co:
        return self.beverage

def intall(dispenser: BeverageDispenser[Juice]) -> None:
    '''Установить автомат для разлива фруктовых соков'''

juice_dispenser = BeverageDispenser(Juice())
install(juice_dispenser)

orange_juice_dispenser = BeverageDispenser(OrangeJuice())
install(orange_juice_dispenser)

# Контрвариантная урна
'''Теперь смоделируем правило по установке урн для мусора. 
Предположим, что еда и напитки поставляются в биоразлагаемых упаковках и пищевые отходы и одноразовые столовые приборы
тоже биоразлагаемые. Урны должны быть пригодны для биоразлагаемых отходов.

Мусор можно организовать в виде простой иерархии:
> Refuse - самый простой тип отходов;
> Biodegradable - специальный тип отходов, который со временем разлагается.
> Compostable - специальный тип биоразлагаемых отходов, который можно эффективно превратить в органическое удобрение
в компостном баке или в установке компостирования.'''

class Refuse:
    '''Любые отходы'''

class Biodegradable(Refuse):
    '''Биоразлагаемые отходы'''

class Compostable(Biodegradable):
    '''Компостируемые отходы'''

T_contra = TypeVar('T_contra', contravariant=True)

class TrashCan(Generic[T_contra]):
    def put(self, refuse: T_contra) -> None:
        '''Хранить отходы, пока не выгружены'''

def deploy(trash_can: TrashCan[Biodegradable]):
    '''Установить урну для биоразлагаемых отходов'''

bio_can: TrashCan[Biodegradable] = TrashCan()
deploy(bio_can)

trash_can: TrashCan[Refuse] = TrashCan()
deploy(trash_can)

