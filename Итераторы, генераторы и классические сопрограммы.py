# Последовательность слов
import re
import reprlib

RE_WORD = re.compile(r'\w+')

class Sentence:
    def __init__(self, text):
        self.text = text
        self.words = RE_WORD.findall(text)

    def __getitem__(self, index):
        return self.words[index]

    def __len__(self):
        return len(self.words)

    def __repr__(self):
        return f'Sentence({reprlib.repr(self.text)})'

s = Sentence('"The time has come," the Walrus said,')
for word in s:
    print(word)
print(list(s))
print(s[2])

# Почему последовательности итерируемы: функция iter
'''
Всякий раз как интерпретатору нужно обойти объект x, он автоматически вызывает функцию iter(x).

Встроенная функций iter выполняет следующие действия.
1. Смотрит, реализует ли объект метод __iter__, и, если да, вызывает его, чтобы получить итератор.
2. Если метод __iter__ не реализован, но реализован метод __getitem__, то Python создает итератор,
который пытается извлекать элементы по порядку, начиная с индекса 0.
3. Если и это не получается, то возбуждается исключение - обычно с сообщением 'C' object is not iterable, 
где C - класс объекта.
'''

# Использование iter в сочетании с Callable
'''
Мы можем вызвать iter() с двумя аргументами, чтобы создать итератор из функции или вообще любого вызываемого объекта.
В таком случае первый аргумент должен быть вызываемым объектом, который будет вызываться многократно (без аргументов)
для порождения значений, а второй - специальным маркером __sentinel: если вызываемый объект возвращает такое значение,
то итератор не отдает его вызывающей стороне, а возбуждает исключение StopIteration.

В примере ниже показано, как можно использовать iter для бросания шестигранной кости до тех пор, пока не выпадет 1.
'''
from random import randint

def d6():
    return randint(1, 6)

d6_iter = iter(d6, 1)

for roll in d6_iter:
    print(roll)

'''
Вторую форму iter() можно с пользой применить для построения читателя блоков.
Например, вот как можно читать блоки фиксированной длины из двоичного файла, до тех пор пока не будет достигнут конец файла.
'''
from functools import partial

with open('floats-10M-lines.txt', 'rb') as file:
    '''Функция partial() необходима, потому что вызываемый объект, переданный iter(), не должен иметь аргументов.'''
    read64 = partial(file.read, 64)
    for block in iter(read64, b''):
        #print(block)
        pass

# Итерируемые объекты и итераторы
'''
Итерируемый объект - любой объект, от которого встроенная функция iter может получить итератор.
Объекты, которые реализуют метод __iter__, возвращающий итератор, являются итерируемыми.
Последовательности всегда итерируемы, поскольку объекты, реализующие метод __getitem__, который принмиает индексы, начинающиеся с нуля.
'''

# Классы Sentence с методом __iter__
# Класс Sentence, попытка №2: классический итератор

RE_WORD = re.compile(r'\w+')

class Sentence:

    def __init__(self, text):
        self.text = text
        self.words = RE_WORD.findall(self.text)

    def __repr__(self):
        return f'Sentence({reprlib.repr(self.text)})'

    def __iter__(self):
        return SentenceIterator(self.words)

class SentenceIterator:

    def __init__(self, words):
        self.words = words
        self.index = 0

    def __next__(self):
        try:
            word = self.words[self.index]
        except IndexError:
            raise StopIteration
        self.index += 1
        return word

    def __iter__(self):
        return self

# Класс Sentence, попытка №3: генераторная функция
class Sentence:

    def __init__(self, text):
        self.text = text
        self.words = RE_WORD.findall(self.text)

    def __repr__(self):
        return f'Sentence({reprlib.repr(self.text)})'

    def __iter__(self):
        for word in self.words:
            yield word
        #return iter(self.words)
        #yield from self.words

# Как работает генератор
def gen_AB():
    print('start')
    yield 'A'
    print('continue')
    yield 'B'
    print('end.')

for c in gen_AB():
    print('--->', c)

# Ленивые классы Sentence
# Класс Sentence, попытка №4: ленивый генератор

RE_WORD = re.compile(r'\w+')

class Sentence:

    def __init__(self, text):
        self.text = text

    def __repr__(self):
        return f'Sentence({reprlib.repr(self.text)})'

    def __iter__(self):
        for match in RE_WORD.finditer(self.text):
            yield match.group()

# Класс Sentence, попытка №5: генераторное выражение
def gen_AB():
    print('start')
    yield 'A'
    print('continue')
    yield 'B'
    print('end.')

res1 = [x * 3 for x in gen_AB()]

for i in res1:
    print('--->', i)

res2 = (x * 3 for x in gen_AB())

for i in res2:
    print('--->', i)

RE_WORD = re.compile(r'\w+')

class Sentence:

    def __init__(self, text):
        self.text = text

    def __repr__(self):
        return f'Sentence({reprlib.repr(self.text)})'

    def __iter__(self):
        return (match.group() for match in RE_WORD.finditer(self.text))

# Генераторные выражения: когда использовать
'''
Сравнение итераторов и генераторов:
Итератор - общий термин, обозначающий любой объект, который реализует метод __next__.
Итераторы предназначены для порождения данных, потребляемых клиентским кодом, т.е. кодом, который управляет 
итератором по-средством цицкла for или другой итеративной конструкции либо путем явного вызова функции next(it) 
для итератора - хотя такое явное использование встречается гораздо реже. 
На практике большинство итераторов, встречающихся в Python, являются генераторами.

Генератор - итератор, построенный компилятором Python. Для создания генератора мы не реализуем метод __next__.
Вместо этого используется ключевое слово yield, в результате чего получаетс генераторная функция, т.е. фабрика объектов-генераторов.
Генераторное выражение - еще один способ построить объект-генератор. 
Объекты-генераторы предоставляют метод __next__, т.е. являются генераторами.
'''

# Генератор арифметической прогрессии

class ArithmeticProgression:

    def __init__(self, begin, step, end=None):
        self.begin = begin
        self.step = step
        self.end = end # None - бесконечный ряд

    def __iter__(self):
        result_type = type(self.begin + self.step)
        result = result_type(self.begin)
        forever = self.end is None
        index = 0
        while forever or result < self.end:
            yield result
            index += 1
            result = self.begin + self.step * index

# Построение арифметической прогрессии с помощью itertools
import itertools

gen = itertools.count(1, .5)
gen = itertools.takewhile(lambda n: n < 3, itertools.count(1, .5))
print(list(gen))

def aritprog_gen(begin, step, end=None):
    first = type(begin + step)(begin)
    ap_gen = itertools.count(begin, step)
    if end is None:
        return ap_gen
    return itertools.takewhile(lambda n: n < end, ap_gen)

# Генераторные функции в стандартной библиотеке (примеры таких функций находятся на странице 577)

# Функции редуцирования итерируемого объекта

