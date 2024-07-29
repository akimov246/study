'''
Метапрограммирование классов - это искусство создания или настройки классов во время выполнения.
'''

# Функция-фабрика классов

from typing import Union, Any
from collections.abc import Iterable, Iterator

FieldNames = Union[str, Iterable[str]] # Пользователь может предоставить имена полей в виде одной строки или итерируемого
                                       # объекта строк

def record_factory(cls_name: str, field_names: FieldNames) -> type(tuple): # Принимаем такие же аргументы, как первые два
                                                                           # в collections.namedtuple; возвращаем type, т.е.
                                                                           # класс, который ведет себя как кортеж

    slots = parse_identifiers(field_names) # Построить кортеж имен атрибутов, он станет атрибутом __slots__ нового класса

    def __init__(self, *args, **kwargs) -> None: # Эта функция станет методом __init__ в новом классе. Она принимает позиционные
                                                 # и (или) именованные аргументы
        attrs = dict(zip(self.__slots__, args))
        attrs.update(kwargs)
        for name, value in attrs.items():
            setattr(self, name, value)

    def __iter__(self) -> Iterator[Any]: # Отдавать значения полей в порядке, определяемом атрибутом __slots__
        for name in self.__slots__:
            yield getattr(self, name)

    def __repr__(self): # Построить удобное представление, обходя __slots__ и __self__
        values = ', '.join(f'{name}={value}' for name, value in zip(self.__slots__, self))
        cls_name = self.__class__.__name__
        return f'{cls_name}({values})'

    cls_attrs = dict( # Построить словарь атрибутов класса
        __slots__=slots,
        __init__=__init__,
        __iter__=__iter__,
        __repr__=__repr__,
    )

    return type(cls_name, (object, ), cls_attrs) # Построить и вернуть новый класс, вызывая конструктор type

def parse_identifiers(names: FieldNames) -> tuple[str, ...]:
    if isinstance(names, str):
        names = names.replace(', ', ' ').split() # Преобразуем строку names, в которой имена разделены пробелами или запятыми,
                                                 # в список строк
    if not all(s.isidentifier() for s in names):
        raise ValueError('names must all be valid identifiers')
    return tuple(names)

Dog = record_factory('Dog', 'name weight owner')
rex = Dog('Rex', 30, 'Bob')
print(rex)

# Введение в __init_subclass__