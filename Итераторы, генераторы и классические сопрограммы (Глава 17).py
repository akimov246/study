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

# yield from и субгенераторы
# Изобретаем chain заново

def chain(*iterables):
    for it in iterables:
        for i in it:
            yield i

print(list(chain('ABC', range(3))))

def chain(*iterables):
    for it in iterables:
        yield from it

print(list(chain('ABC', range(3))))

# Обход дерева

def tree(cls):
    yield cls.__name__, 0
    for sub_cls in cls.__subclasses__():
        yield sub_cls.__name__, 1

def display(cls):
    for cls_name, level in tree(cls):
        indent = ' ' * 4 * level
        print(f'{indent}{cls_name}')

display(BaseException)

def tree(cls):
    yield cls.__name__, 0
    yield from sub_tree(cls)

def sub_tree(cls):
    for sub_cls in cls.__subclasses__():
        yield sub_cls.__name__, 1

def display(cls):
    for cls_name, level in tree(cls):
        indent = ' ' * 4 * level
        print(f'{indent}{cls_name}')

display(BaseException)

def tree(cls):
    yield cls.__name__, 0
    yield from sub_tree(cls)

def sub_tree(cls):
    for sub_cls in cls.__subclasses__():
        yield sub_cls.__name__, 1
        for sub_sub_cls in sub_cls.__subclasses__():
            yield sub_sub_cls.__name__, 2

def display(cls):
    for cls_name, level in tree(cls):
        indent = ' ' * 4 * level
        print(f'{indent}{cls_name}')

display(BaseException)

def tree(cls):
    yield cls.__name__, 0
    yield from sub_tree(cls)

def sub_tree(cls):
    for sub_cls in cls.__subclasses__():
        yield sub_cls.__name__, 1
        for sub_sub_cls in sub_cls.__subclasses__():
            yield sub_sub_cls.__name__, 2
            for sub_sub_sub_cls in sub_sub_cls.__subclasses__():
                yield sub_sub_sub_cls.__name__, 3

def display(cls):
    for cls_name, level in tree(cls):
        indent = ' ' * 4 * level
        print(f'{indent}{cls_name}')

display(BaseException)

def tree(cls):
    yield cls.__name__, 0
    yield from sub_tree(cls, 1)

def sub_tree(cls, level):
    for sub_cls in cls.__subclasses__():
        yield sub_cls.__name__, level
        yield from sub_tree(sub_cls, level + 1)

def display(cls):
    for cls_name, level in tree(cls):
        indent = ' ' * 4 * level
        print(f'{indent}{cls_name}')

display(BaseException)

def tree(cls, level = 0):
    yield cls.__name__, level
    for sub_cls in cls.__subclasses__():
        yield from tree(sub_cls, level + 1)

def display(cls):
    for cls_name, level in tree(cls):
        indent = ' ' * 4 * level
        print(f'{indent}{cls_name}')

display(BaseException)

# Обобщенные итерируемые типы
from collections.abc import Iterable
from typing import TypeAlias

FROM_TO: TypeAlias = tuple[str, str]

def zip_replace(text: str, changes: Iterable[FROM_TO]) -> str:
    for from_, to in changes:
        text = text.replace(from_, to)
    return text

from collections.abc import Iterator

def fibonacci() -> Iterator[int]:
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b

# Классические сопрограммы
'''
Сопрограмма - это генераторная функция, в теле которой имеется ключевое слово yield.

Объект сопрограммы является объектом-генератором.

> Генераторы порождаю данные для итерирования;
> Сопрограммы являются потребителями данных;
> Сопрограммы не имеют никакого отношения к итерированию;
'''

# Пример: сопрограмма для вычисления накопительного среднего
from collections.abc import Generator

def averager() -> Generator[float, float, None]: # Generator[YieldType, SendType, ReturnType]
    total = 0.0
    count = 0
    average = 0.0
    while True:
        term = yield average
        total += term
        count += 1
        average = total / count

'''
В этом тесте вызов next(coro_avg) заставляет сопрограмму дойти до yield, при этом будет отдано начальное значение average.
Запустить программу можно также, вызвав coro_avg.send(None), - именно так и поступает встроенная фунцкия next().
Но отправить какое-то значение, кроме None, нельзя, потому что сопрограмма может принимать отправленные значения,
только когда приостановлена в точке yield. Вызов next() или .send(None), чтобы продвинуть выполнение к первому
предложению yield, называется "инициализацией сопрограммы".
'''

coro_avg = averager()
#coro_avg.send(None)
next(coro_avg)
print(coro_avg.send(10))
print(coro_avg.send(20))
coro_avg.close() # Метод .close() используется для явного завершения генератора

# Возврат знаения из сопрограммы
from collections.abc import Generator
from typing import Union, TypeAlias
from dataclasses import dataclass

@dataclass
class Result:
    count: int
    average: float

class Sentinel:
    def __repr__(self):
        return f'<Sentinel>'

STOP = Sentinel()

#SendType = Union[float, Sentinel]
SendType: TypeAlias = float | Sentinel

def averager2(verbose: bool=False) -> Generator[None, SendType, Result]:
    total = 0.0
    count = 0
    average = 0.0
    while True:
        term = yield
        if verbose:
            print('received:', term)
        if isinstance(term, Sentinel):
            break
        total += term
        count += 1
        average = total / count
    return Result(count, average)

coro_avg = averager2()
next(coro_avg)
coro_avg.send(10)
coro_avg.send(30)
coro_avg.send(6.5)
try:
    coro_avg.send(STOP)
except StopIteration as exc:
    result = exc.value

print(result)

def compute():
    res = yield from averager2(True)
    print('computed', res)
    return res

comp = compute()
for v in [None, 10, 20, 30, STOP]:
    try:
        comp.send(v)
    except StopIteration as exc:
        result = exc.value