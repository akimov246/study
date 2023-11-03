#bytes - неизменяемый
#bytearray - изменяемый
import codecs
import os
import sys

import winioctlcon

cafe = bytes("café", encoding="utf8")
print(cafe[0])
print(cafe[:1])
cafe_arr = bytearray(cafe)
print(cafe_arr[0])
print(cafe_arr[:1])

print()

import array
numbers = array.array("h", [-2, -1, 0, 1, 2])
octets = bytes(numbers)
print(octets)

for codec in ["latin_1", "utf_8", "utf_16"]:
    print(codec, "El Niño".encode(codec))

print()

#Обработка UnocodeEncodeError и UnicodeDecodeError
print("São Paulo".encode("cp437", errors="replace"))

def codec_err(e):
    return "8", e.start + 1

codecs.register_error("my_error", codec_err)
print("São Paulo".encode("cp437", errors="my_error"))
#Если str состоит на 100% из ASCII символов, то его можно представить в виде байтов в любой кодировке
print("Akimov Leonid".isascii())

# chardet - модуль, позволяющий определить кодировку последовательности байт

print()

# Всегда стоит явно указывать кодировку при записи/чтении файлов.
open("./cafe.txt", "w", encoding="utf-8").write("café")
print(open("./cafe.txt", "r", encoding="utf-8").read())
os.remove("./cafe.txt")

print()

# Нормализация Unicode для надежного сравнения
from unicodedata import normalize
s1 = "café"
s2 = "cafe\N{COMBINING ACUTE ACCENT}"
print(len(s1), len(s2))
# NFC - производит композицию двух кодовых позиций с целью получения самой короткой эквиватентной строки
# NFD - произвводит декомпозицию, т.е. разложение составного символа на базовый и модифицирующие
print(len(normalize("NFC", s1)), len(normalize("NFC", s2)))
print(len(normalize("NFD", s1)), len(normalize("NFD", s2)))
print(s1 == s2)
print(normalize("NFC", s1) == normalize("NFC", s2))
print(normalize("NFD", s1) == normalize("NFD", s2))
# Для сравнения строк без учета регистра используется метод casefold

# Экстремельная "нормализация": удаление диакритических знаков
import unicodedata

def shave_marks(txt):
    """Remove all diacritic marks"""
    norm_text = unicodedata.normalize("NFD", txt)
    shaved = "".join(c for c in norm_text if not unicodedata.combining(c))
    return unicodedata.normalize("NFC", shaved)

order = "Herr Voß: • ½ cup of OEtker™ caffè latte • bowl of açaí."
print(shave_marks(order))

print()

# Сортировка Unicode-текстов
# Лучше всего использовать эту библиотеку для соортировки неанглийских текстов
from pyuca import Collator
c = Collator()
fruits = ['caju', 'atemoia', 'cajá', 'açaí', 'acerola']
print(sorted(fruits, key=c.sort_key))

print()

# Поиск символа по имени
print(unicodedata.name("☻"))

# Функция для поиска символов
START, END = ord(" "), sys.maxunicode + 1

def find(*query_words, start=START, end=END):
    query = {w.upper() for w in query_words}
    for code in range(start, end):
        char = chr(code)
        name = unicodedata.name(char, None)
        if name and query.issubset(name.split()):
            print(char, name)
            print(f'U+{code:04X}\t{char}\t{name}')

l = ["black", "face"]
find(*l)

# Символы связанные с числами
import unicodedata
import re

re_digit = re.compile(r"\d")
sample = '1\xbc\xb2\u0969\u136b\u216b\u2466\u2480\u3285'

for char in sample:
    print(f"U+{ord(char):04x}",
          char.center(6),
          "re_dig" if re_digit.match(char) else "-",
          "isdig" if char.isdigit() else "-",
          "isnum" if char.isnumeric() else "-",
          f"{unicodedata.numeric(char):5.2f}", # Числовое значение в поле шириной 5 с двумя знаками после запятой
          unicodedata.name(char),
          sep="\t")

# str и bytes в регулярных выражениях
re_numbers_str = re.compile(r"\d+")
re_words_str = re.compile(r"\w+")
re_numbers_bytes = re.compile(rb"\d+")
re_words_bytes = re.compile(rb"\w+")

text_str = "Ramanujan saw \u0be7\u0bed\u0be8\u0bef as 1729 = 1³ + 12³ = 9³ + 10³."
text_bytes = text_str.encode("utf-8")

print(f"Text\n {text_str}")
print("Numbers")
print("str: ", re_numbers_str.findall(text_str))
print("bytes: ", re_numbers_bytes.findall(text_bytes))
print("Words")
print("str: ", re_words_str.findall(text_str))
print("bytes: ", re_words_bytes.findall(text_bytes))

# str и bytes в функциях из модуля os
print(os.listdir("."))
print(os.listdir(b"."))
print(os.fsdecode(os.listdir(b".")[8]))