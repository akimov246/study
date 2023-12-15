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