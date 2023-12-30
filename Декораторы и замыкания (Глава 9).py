# КРАТКОЕ ВВЕДЕНИЕ В ДЕКОРАТОРЫ
# Декоратор - это вызываемый объект, который принимает другую функцию в качестве аргумента
# Декоратор - это функция или другой вызываемый объект
# Декоратор может заменить декорируемыую функцию другой
# Декораторы выполняются сразу после загрузки модуля

# КОГДА PYTHON ВЫПОЛНЯЕТ ДЕКОРАТОРЫ
registry = []

def register(func):
    print(f"running register({func})")
    registry.append(func)
    return func

@register
def f1():
    print("rinning f1()")

@register
def f2():
    print('running f2()')

def f3():
    print('running f3()')

def main():
    print('running main()')
    print('registry ->', registry)
    f1()
    f2()
    f3()

if __name__ == '__main__':
    main()

# РЕГИСТРАЦИОННЫЕ ДЕКОРАТОРЫ
# Декораторы обычно определяются в одном модуле и применяются к функциям из других модулей

# ЗАМЫКАНИЯ
# Замыкание - это функция с расширенной областью видимости, которая охватывает переменные,
# на которые есть ссылки в теле функции, но которые не являются ни глобальными, ни локальными переменными функции.
# Такие перменные должны происходить из локальной области видимости внешней функции, объемлющей нашу функцию.

class Averager:

    def __init__(self):
        self.series = []

    def __call__(self, new_value: int) -> float:
        self.series.append(new_value)
        return sum(self.series) / len(self.series)

avg = Averager()
print(avg(10))
print(avg(1488))

def make_averager():
    series = []

    def averager(new_value):
        series.append(new_value) # свободная переменная, т.е. переменная не связанная с локальной областью видимости
        return sum(series) / len(series)

    return averager

avg = make_averager()
print(avg(10))
print(avg(1488))
print(avg.__code__.co_varnames)
print(avg.__code__.co_freevars)
print(avg.__closure__)
print(avg.__closure__[0].cell_contents)

"""
Замыкание - это функция, которая запоминает привязки свободных перменных, существовавшие
на момент определения функции, так что их можно использовать впоследствии при вызове функции,
когда область видимости, в которой она была определена, уже не существует
"""

# ОБЪЯВЛЕНИЕ NONLOCAL
"""
nonlocal позволяет пометить переменную, как свободную, даже если ей присваивается новое значение внутри функции
"""

def make_avareger():
    count = 0
    total = 0

    def averager(new_value):
        nonlocal count, total
        count += 1
        total += new_value
        return total / count

    return averager

avg = make_avareger()
print(avg(10))
print(avg(1488))

# РЕАЛИЗАЦИЯ ПРОСТОГО ДЕКОРАТОРА
import time

# Данный декоратор имеет ряд недостатков:
# - Не поддерживает именованные аргументы
# - Маскирует аттрибуты __name__ и __doc__ декорированной функции
def clock(func):
    def clocked(*args):
        start = time.perf_counter()
        result = func(*args)
        lead_time = time.perf_counter() - start
        name = func.__name__
        arg_str = ", ".join(str(arg) for arg in args)
        print(f"[{lead_time:.8f}s] {name}({arg_str}) -> {result}")
        return result

    return clocked

@clock
def snooze(seconds):
    time.sleep(seconds)

@clock
def factorial(n):
    return 1 if n < 2 else n*factorial(n - 1)

if __name__ == '__main__':
    print('*'*40, 'Calling snooze(.123)')
    snooze(.123)
    print('*'*40, 'Calling factorial(6)')
    print('6! =', factorial(6))

# Улучшенный декоратор clock с помощью @functools.wraps:
# - Копирует аттрибуты __name__ и __doc__ из func в clocked
# - Правильно обрабатываются именованные аргументы
import functools

def clock(func):
    @functools.wraps(func)
    def clocked(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        lead_time = time.perf_counter() - start
        name = func.__name__
        arg_lst = [str(arg) for arg in args]
        arg_lst.extend([f'{k}={v}' for k, v in kwargs.items()])
        arg_str = ', '.join(arg_lst)
        print(f'[{lead_time:.8f}] {name}({arg_str}) -> {result}')
        return result
    return clocked

@clock
def test(name: str, surname: str):
    return f"{name.capitalize()} {surname.capitalize()}"

if __name__ == '__main__':
    print('*'*40, f'Calling test(name=\'леонид\', surname=\'акимов\')')
    print(test(name='леонид', surname='акимов'))

# ДЕКОРАТОРЫ В СТАНДАРТНОЙ БИБЛИОТЕКЕ
# ЗАПОМИНАНИЕ С ПОМОЩЬЮ functools.cache
"""
Декораторы cache, lru_cache реализуют запоминание (memoization): прием оптимизации, смысл которого заключается в сохранении
результатов предыдущих дорогостоящих вызовов функции, что позволяет избежать повторного вычисления с теми же аргументами, что и раньше.
"""


@clock
def fibonacci(n):
    if n < 2:
        return n
    return fibonacci(n - 2) + fibonacci(n - 1)

if __name__ == '__main__':
    print(fibonacci(6))

import functools

@functools.cache
@clock
def fibonacci(n):
    if n < 2:
        return n
    return fibonacci(n - 2) + fibonacci(n - 1)

if __name__ == '__main__':
    print(fibonacci(6))

"""
functools.cache может занять всю имеющуюся память, если в кэше очень много элементов.
Данный декоратор стоит использовать только в командных скриптах, работающих недолго.
Для долгоживущих процессов стоит использовать functools.lru_cache с параметром maxsize.
"""

# ИСПОЛЬЗОВАНИЕ lru_cache
@functools.lru_cache #maxsize=128, typed=False
def test(a, b):
    pass

@functools.lru_cache(maxsize=2**20, typed=True)
def test(a, b):
    pass

"""
При maxsize=None lru_cache начинает работать, как cache
typed=True определяет, стоит ли хранить элементы разного типа раздельно.
Например, в конфигурации по умолчанию (typed=False) элементы типа float и int, признаные равными,
хранятся лишь один раз, т.е. вызовы f(1) и f(1.0) приведут к помещению в кеш только одного элемента.
"""

# ОБОБЩЕННЫЕ ФУНКЦИИ С ОДИНОЧНОЙ ДИСПЕТЧЕРИЗАЦИЕЙ
# Функция singledispatch
"""
Декоратор functools.singledispatch позволяет каждому модулю вносить свой вклад в решение,
так что пользователь легко может добавить специализированную функцию, даже не имея возможности изменять класс.
Обычная функция, декорированная @singledispatch, становится точкой входа для обобщенной функции:
группы функций, выполняющих одну и ту же логическую операцию по-разному в зависимости от типа первого аргумента.
Именно это и называется одиночной диспетчеризацией. Если бы для выбора конкретных функций использовалось больше аргументов,
то мы имели бы множественную диспетчеризацию.
"""

from functools import singledispatch
from collections import abc
import fractions
import decimal
import html
import numbers

@singledispatch # Помечает базовую функцию, которая обрабатывает тип object
def htmlize(obj: object) -> str:
    content = html.escape(str(obj))
    return f'<pre>{content}</pre>'

@htmlize.register # Каждая специализированная функция снабжается декоратором @"base".register
def _(text: str) -> str: # Тип первого аргумент, переданного во время выполнения, определяет, когда будет использоваться это конкретное определение функции
    content = html.escape(text).replace('\n', '<br/>\n')
    return f'<p>{content}</p>'

@htmlize.register
def _(seq: abc.Sequence) -> str: # Для каждого типа, нуждающегося в специальной обработке, регистрируется новая функция с подходящей аннотацией типа в первом параметре
    inner = '</li>\n<li>'.join(htmlize(item) for item in seq)
    return '<ul>\n<li>' + inner + '</li>\n</ul>'

@htmlize.register
def _(n: numbers.Integral) -> str:
    #return f'<pre>{n} ({hex(n)})</pre>'
    return f'<pre>{n} (0x{n:x})</pre>'

@htmlize.register
def _(n: bool) -> str:
    '''bool является подтипом numbers.Integral, но singledispatch ищет реализацию с самым специфичным
        подходящим типом независимо от порядка появления в программе'''
    return f'<pre>{n}</pre>'

@htmlize.register(fractions.Fraction)
def _(x) -> str:
    '''Если вы не хотите или не можете добавить аннотации типов в декорированную функцию, то можете
        передать тип декоратору @"base".register'''
    frac = fractions.Fraction(x)
    return f'<pre>{frac.numerator}/{frac.denominator}</pre>'

@htmlize.register(decimal.Decimal)
@htmlize.register(float)
def _(x) -> str:
    '''Декоратор @"base".register возвращает недекорированную функцию,
        поэтому можно компоновать их, чтобы зарегистрировать два или более типов для одной и той же реализации'''
    frac = fractions.Fraction(x).limit_denominator()
    return f'<pre>{x} ({frac.numerator}/{frac.denominator})</pre>'

'''
Если есть возможность, регистрируйте специализированные функции для обработки ABC (абстрактных классов),
например numbers.Integral или abc.MutableSequence, а не конкретных реализаций, например int или list.
Это позволит программе поддержать более широкий спектр совместимых типов. 
Например, расширение Python может предоставлять альтернативу типу int с фиксированной длиной в битах в качестве 
подклассов numbers.Integral
'''

# ПАРАМЕТРИЗОВАННЫЕ ДЕКОРАТОРЫ
registry = []

def register(func):
    print(f'running register({func})')
    registry.append(func)
    return func

@register
def f1():
    print('running f1()')

print('running main()')
print('registry ->', registry)

# ПАРАМЕТРИЗОВАННЫЙ РЕГИСТРАЦИОННЫЙ ДЕКОРАТОР
registry = set() # Заменим list на set, чтобы ускорить добавлений и удалений функций

def register(active=True): # Функция register принимает необязательный именованный аргумент (фабрика декораторов)
    def decorate(func): # Именно эта функция является декоратором
        print(f'running register(active={active})->decorate({func})')
        if active: # Регистрируем func, если аргумент active равен True
            registry.add(func)
        else: # Если не active и функция func присутствует в registry, удаляем ее
            registry.discard(func)

        return func
    return decorate

@register(active=False)
def f1():
    print('running f1()')

@register()
def f2():
    print('running f2()')

def f3():
    print('running f3()')

# ПАРАМЕТРИЗОВАННЫЙ ДЕКОРАТОР clock
DEFAULT_FMT = '[{elapsed:.8f}s] {name}({args}) -> {result}'

def clock(fmt=DEFAULT_FMT): # Фабрика параметризованных декораторов
    def decorate(func): # Декоратор (принимает функцию и возвращает фунцию-обертку)
        def clocked(*_args): # Функция-обертка
            start = time.perf_counter()
            _result = func(*_args) # Результат, возвращенный декорированной функцией
            elapsed = time.perf_counter() - start
            name = func.__name__
            args = ', '.join(str(arg) for arg in _args)
            result = str(_result)
            print(fmt.format(**locals())) # Подставляем в fmt все локальные переменные функции clocked
            return _result
        return clocked
    return decorate

if __name__ == '__main__':
    @clock()
    def snooze(seconds):
        time.sleep(seconds)

    for i in range(3):
        snooze(.123)

# ДЕКОРАТОР clock НА ОСНОВЕ КЛАССОВ
DEFAULT_FMT = '[{elapsed:.8f}s] {name}({args}) -> {result}'

class clock: # Фабрика параметризованных декораторов

    def __init__(self, fmt=DEFAULT_FMT):
        self.fmt = fmt

    def __call__(self, func): # Декоратор
        def clocked(*_args): # Обертка
            start = time.perf_counter()
            _result = func(*_args)
            elapsed = time.perf_counter() - start
            name = func.__name__
            args = ', '.join(str(arg) for arg in _args)
            result = str(_result)
            print(self.fmt.format(**locals()))
            return _result
        return clocked

@clock('{name}: {elapsed}')
def snooze(seconds):
    time.sleep(seconds)

for i in range(3):
    snooze(.123)