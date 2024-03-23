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
