# Контекстные менеджеры и блоки with

with open('text.txt', 'rb') as file:
    src = file.read(60).decode('utf-8')

'''
Интерфейс контекстного менеджера состоит из методов __enter__ и __exit__.
В начале блока with вызывается метод __enter__ контекстного менеджера. Когда блок with завершается естественным или иным образом,
Python вызывает метод __exit__ контекстного менеджера.
'''

# Класс контекстного менеджера LookingGlass
import sys

class LookingGlass:

    def __enter__(self):
        self.original_write = sys.stdout.write
        sys.stdout.write = self.reverse_write # Подменяем метод sys.stdout.write своим собственным
        return 'JABBERWOCKY' # Это значение вернется в переменную what после as

    def reverse_write(self, text):
        self.original_write(text[::-1])

    def __exit__(self, exc_type, exc_value, traceback):
        '''Python вызывает метод __exit__ с аргументами None, None, None, если не было ошибок;
        если же имело место исключение, то в аргументах передаются данные об исключении:
        ext_type - Класс исключения
        ext_value - Объект исключения. Иногда в атрибуте exc_value.args можно найти параметры,
        переданные конструктору исключения, например сообщение об ошибке.
        traceback - traceback
        '''
        sys.stdout.write = self.original_write # Восстанавливаем исходный метод sys.stdout.write
        if exc_type is ZeroDivisionError:
            '''Если исключение было и его тип - ZeroDivisionError, то напечатаем сообщение...'''
            print('Please DO NOT divide by zero!')
            return True # Возвращаем True, уведомляя интерпретатор о том, что исключение обработано
        # Если метод __exit__ возвращает None или что-то, похожее на False, то исключение, возникшее внутри блока with,
        # распространяется дальше.


with LookingGlass() as what:
    print('Alice, Kitty and Snowdrop')
    print(what)

print(what)

manager = LookingGlass()
monster = manager.__enter__()
print(monster == 'JABBERWOCKY')
print(monster)
manager.__exit__(None, None, None)
print(monster)

# Утилиты contextlib
# Использование @contextmanager
'''
Декоратор @contextmanager - элегантный и практичный инструмент, объединяющий три разных средства Python:
декоратор функции, генератор и предложение with.
Использование @contextmanager уменьшает объем стереотипного кода создания контекстного менеджера:
вместо того, чтобы писать целый класс с методами __enter__/__exit__, мы просто реализуем генератор с одним
предложением yield, порождающим значение, которое должен вернуть метод __enter__.
Если генератор снабжем декоратором @contextmanager, то yield разбивает тело функции на две части:
все, что находится до yield, используется в начале блока with, когда интерпретатор вызывает метод __enter__;
а все, что находится после yield, выполняется при вызове метода __exit__ в конце блока.
'''

import contextlib
import sys

@contextlib.contextmanager
def looking_glass():
    original_write = sys.stdout.write

    def reverse_write(text):
        original_write(text[::-1])

    sys.stdout.write = reverse_write
    msg = ''
    try:
        yield 'JABBERWOCKY'
    except ZeroDivisionError:
        msg = 'Please DO NOT divide by zero!'
    finally:
        sys.stdout.write = original_write
        if msg:
            print(msg)

with looking_glass() as what:
    print('Alice, Kitty and Snowdrop')
    print(what)
    print(5 / 0)

print(what)

# Делай то, потом это: блоки else вне if
'''
> for:
Блок else выполняется, только если цикл for дошел до конца (т.е. не было преждевременного выхода с помощью break)

> while:
Блок else выполняется, только если цикл while завершился вследствии того, что условие приняло ложное значение
(а не в результате выхода с помощью break)

> try:
Блок else выполняется, только если в блоке try не возникло исключение.
Исключения, возникшие в части else, не обрабатываются в предшествующих частях except.

В любом случае часть else не выполняется и тогда, когда исключение либо одно из предложений, return, break или continue, 
приводят к передаче управления вовне главного блока составного предложения.
'''

from dataclasses import dataclass

@dataclass
class Juice:
    flavor: str
    availability: bool

my_list = [Juice('apple', True), Juice('orange', False)]

for item in my_list:
    if item.flavor == 'banana':
        break
else:
    #raise ValueError('No banana flavor found!')
    pass

import time

class Timer:

    def __enter__(self):
        self.start = time.time()

    def __exit__(self, exc_type, exc_val, exc_tb):
        print(f'{time.time() - self.start:.2f}')

with Timer():
    print('Зашли в блок with')
    time.sleep(2)
    print('Функция отработала')