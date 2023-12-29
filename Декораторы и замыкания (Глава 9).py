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