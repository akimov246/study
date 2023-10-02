#bytes - неизменяемый
#bytearray - изменяемый
import codecs
import os

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