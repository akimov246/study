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

from collections.abc import Callable
from typing import Any, NoReturn, get_type_hints

class Field:
    def __init__(self, name: str, constructor: Callable) -> None:
        if not callable(constructor) or constructor is type(None):
            raise TypeError(f'{name} type hint must be callable')
        self.name = name
        self.constructor = constructor

    def __set__(self, instance: Any, value: Any) -> None:
        if value is ...: # Если Checked.__init__ присваивает value значение ... (встроенный объект Ellipsis), то мы
                         # вызываем constructor без аргументов
            value = self.constructor()
        else:
            try:
                value = self.constructor(value) # В противном случае вызываем constructor с заданным значением value
            except (TypeError, ValueError) as e: # Если constructor возбуждает одно из этих исключений, то возбуждаем
                                                 # TypeError с содержательным сообщением
                type_name = self.constructor.__name__
                msg = f'{value} is not compatible with {self.name}:{type_name}'
                raise TypeError(msg) from e
            instance.__dict__[self.name] = value # Если исключений не было, то value сохраняется в instance.__dict__

class Checked:
    @classmethod
    def _fields(cls) -> dict[str, type]:
        return get_type_hints(cls)

    def __init_subclass__(subclass) -> None:
        super().__init_subclass__()
        for name, constructor in subclass._fields().items():
            setattr(subclass, name, Field(name, constructor))

    def __init__(self, **kwargs: Any) -> None:
        for name in self._fields():
            value = kwargs.pop(name, ...)
            setattr(self, name, value)
        if kwargs:
            self.__flag_unknown_attrs(*kwargs)

    def __setattr__(self, name: str, value: Any) -> None: # Перехватывать все попытки установить атрибут экземпляра.
                                                          # Необходимо, чтобы предотвратить присваивание неизвестному атрибуту
        if name in self._fields(): # Если атрибут с именем name известен, получить соответствующий дескриптор.
            cls = self.__class__
            descriptor = getattr(cls, name)
            descriptor.__set__(self, value)
        else:
            self.__flag_unknown_attrs(name)

    def __flag_unknown_attrs(self, *names: str) -> NoReturn:
        plural = 's' if len(names) > 1 else ''
        extra = ', '.join(f'{name}' for name in names)
        cls_name = repr(self.__class__.__name__)
        raise AttributeError(f'{cls_name} object has no attribute{plural} {extra}')

    def _asdict(self) -> dict[str, Any]:
        return {
            name: getattr(self, name)
            for name, attr in self.__class__.__dict___.items()
            if isinstance(attr, Field)
        }

    def __repr__(self) -> str:
        kwargs = ', '.join(f'{key}={value}' for key, value in self._asdict().items())
        return f'{self.__class__.__name__}({kwargs})'

# Дополнение класса с помощью декоратора класса
'''
Декоратор класса - это вызываемый объект, который ведет себя, как декоратор функции: получает декорированный класс в качестве
аргумента и возвращает заменяющий его класс. Часто декорораторы классов возвращают сам декорированный класс после внедрения 
в него новых методов с помощью присваивания атрибутам.
'''

# Что когда происходит: этам импорта и этап выполнения
'''
На этапе импорта интерпретатор:
1. Производит синтаксический анализ исходного кода py-модуля сверху вниз. Именно в это время могут возникнуть исключения SyntaxError;
2. Генерирует исполняемый байт-код;
3. Выполняет код верхнего уровня откомпилированного модуля.
'''