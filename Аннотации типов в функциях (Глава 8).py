import typing
from typing import Optional

def show_count(count: int, word: str, plural: Optional[str] = None) -> str:
    if count == 1:
        return f"{count} {word}"
    str_count = str(count) if count else "no"
    if not plural:
        plural = word + "s"
    return f"{str_count} {plural}"

print(show_count(99, "bird"))

# Аннотация для кортежа неопределенной длины
def mutable_tuble(t: tuple[str, ...]):
    return t

# Функция, преобразующая последовательность в таблицу
from collections.abc import Sequence

def columnize(sequence: Sequence[tuple[str, ...]], num_columns: int = 0):
    if num_columns == 0:
        num_columns = round(len(sequence) ** 0.5)
    num_rows, reminder = divmod(len(sequence), num_columns)
    num_rows += bool(reminder)
    return [tuple(sequence[i::num_rows] for i in range(num_rows))]

# Функция, позволяющая найти символ Unicode в диапазоне индексов
import sys
import re
import unicodedata

from collections.abc import Iterator

RE_WORD = re.compile("\w+")
STOP_CODE = sys.maxunicode + 1

def tokenize(text: str) -> Iterator[str]:
    """Вернуть итерируемый объект, содержащий слова в верхнем регистре"""
    for match in RE_WORD.finditer(text):
        yield match.group().upper()

def name_index(start: int = 32, end: int = STOP_CODE) -> dict[str, set[str]]:
    index: dict[str, set[str]] = {}
    for char in (chr(i) for i in range(start, end)):
        if name := unicodedata.name(char, ""):
            for word in tokenize(name):
                index.setdefault(word, set()).add(char)
    return index

index = name_index(32, 1488)
print(index)
print(index["EIGHT"] & index["DIGIT"])

# Для аннотирования аргументов, представляющих из себя отображения, лучше использовать Mapping или MutableMapping вместо dict
# И Sequence или Iterable из модуля collections.abs для аргументов: list, tuple, set.
# Sequence лучше использовать, когда важно знать длину принимаемого параметра
# Iterable же, когда параметр необходимо обработать целиком, вне зависимости от его длины.

# Примеры аргумента типа Iterable
from collections.abc import Iterable

def fsum_(__seq: Iterable[float]) -> float:
    """Функция из модуля math"""
    pass

l33t = [("a", "4"), ("e", "3"), ("i", "1"), ("o", "0")]
text = "mad skilled noob powned leet"

from typing import TypeAlias # Явные псевдонимы типов. Рекомендуется указывать тип TypeAlias для псевдонимов типов.
FromTo: TypeAlias = tuple[str, str] # Псевдоним типа, чтобы было проще читать сигнатуру функции

def zip_replace(text: str, changes: Iterable[FromTo]) -> str:
    for from_, to in changes:
        text = text.replace(from_, to)
    return text

print(zip_replace(text, l33t))

# Параметризованные обобщенные типы и TypeVar
from collections.abc import Sequence
from random import shuffle
from typing import TypeAlias, TypeVar

T: TypeAlias = TypeVar("T")

def sample(population: Sequence[T], size: int) -> list[T]:
    if size < 1:
        raise ValueError("size must be >= 1")
    result = list(population)
    shuffle(result)
    return result[:size]

# Ограниченный TypeVar
from collections.abc import Iterable
from decimal import Decimal
from fractions import Fraction
from typing import TypeAlias, TypeVar

NumberT: TypeAlias = TypeVar("NumberT", Decimal, Fraction, float)
def mode(data: Iterable[NumberT]) -> NumberT:
    """Значения параметров могут быть типами: Decimal, Fraction, float"""
    pass

# Связанный TypeVar
from collections import Counter
from collections.abc import Iterable, Hashable
from typing import TypeAlias, TypeVar

# Параметр bound задает верхнюю границу допустимых типов.
# Конкретно в этом примере это означает, что параметр-тип может быть Hashable или любым его подтипом.
# Короче говоря, элементы итерируемого объекта должны быть хэшируемого типа
HashableT: TypeAlias = TypeVar("HashableT", bound=Hashable)

def mode(data: Iterable[HashableT]) -> HashableT:
    pairs = Counter(data).most_common(1)
    if len(pairs) == 0:
        raise ValueError("no mode for empty data")
    return pairs[0][0]

from typing import AnyStr
# AnyStr = TypeVar("AnyStr", str, bytes)

# Статические протоколы
# Пример Протокола, ограничивающего параметры типами реализующими метод __lt__ (меньше).
from typing import Protocol, Any

class SupportsLessThan(Protocol):
    def __lt__(self, other: Any) -> bool:
        pass

from collections.abc import Iterable
from typing import TypeVar

LT = TypeVar("LT", bound=SupportsLessThan)

def top(series: Iterable[LT], length: int) -> list[LT]:
    ordered = sorted(series, reverse=True)
    return ordered[:length]

fruits = 'mango pear apple kiwi banana'.split()
print(top(fruits, 3))
series = [object() for _ in range(4)]
#print(top(series, 3)) # Выдаст ошибку, да и ошибка сразу подсвечивается

# Домашнее задание от Илюхи Жопича (ответ будет в 13 главе)
from typing import Protocol, TypeVar

T = TypeVar('T')

class SupportsMul(Protocol):
    def __mul__(self: T, other: int) -> T:
        pass

SM = TypeVar("SM", bound=SupportsMul)

def double(x: SM) -> SM:
    return x * 2

print(double(1488))

# Тип Callable
from collections.abc import Callable
# Список параметров может содержать нуль или более типов
#Callable[[ParamType1, ParamType2], ReturnType]
# Если вам нужна аннотация типа для функции с гибкой сигнатурой, замените весь список параметров многточием:
# Callable[..., ReturnType]

# Тип NoReturn
# Примером такого типа является функция exit. Сигнатура функции exit:
def exit_(__status: object = ...):
    pass

def test(x = ...):
    print(x)

print(test())