# Представления объекта
'''
repr() - Вернуть строку, представляющую объект в виде, удобном для разработчика.
Это то, что мы видим, когда объект отображается на консоли Python или в отладчике.

str() - Вернуть строку, представляющую объект в виде, удобном для пользователя.
Это то что печатает функция print().

bytes() - Получить представление объекта в виде последовательности байтов.

format() - Вызывается f-строками, встроенной функцией format() и методом str.format() для получения
строкового представления объектов с помощью специальных форматных кодов.
'''

from array import array
import math

# Класс вектора
class Vector2d:
    '''Чтобы заставить работать класс с позиционными образцами (match/case), необходимо добавить атрибут класса __match_args__,
       перечислив в нем атрибуты экземпляра в том порядке, в каком они будут использоваться при позиционном сравнении с образцом.
    '''
    __match_args__ = ('x', 'y')

    typecode = 'd' # Аттрибут класса, которым мы воспользуемся, когда будем преобразовывать экземпляры Vector2d в последовательность байтов и наоборот.

    def __init__(self, x, y):
        self.__x = float(x)
        self.__y = float(y)

    # Декоратор @property спользуется для создания свойства чтения закрытого атрибута класса
    @property
    def x(self):
        return self.__x

    @property
    def y(self):
        return self.__y

    # Декоратор x.setter задает setter для защищенного атрибута класса (его тут быть не должно, для примера добавил)
    @x.setter
    def x(self, value):
        self.__x = float(value)

    def __iter__(self):
        '''Наличие метода __iter__ делает Vector2d итерируемым;
           Именно благодаря ему работает распаковка (например, x, y = my_vector).
        '''
        return (i for i in (self.x, self.y))

    def __repr__(self):
        class_name = type(self).__name__
        return '{}({!r}, {!r})'.format(class_name, *self)
        #return f'{class_name}{self.x, self.y}'

    def __str__(self):
        '''Из итерируемого объекта легко построить кортеж для отображения в виде упорядоченной пары'''
        return str(tuple(self))

    def __bytes__(self):
        return (bytes([ord(self.typecode)]) +
                bytes(array(self.typecode, self)))

    def __eq__(self, other):
        return tuple(self) == tuple(other)

    def __abs__(self):
        return math.hypot(self.x, self.y)

    def __bool__(self):
        return bool(abs(self))

    @classmethod
    def frombytes(cls, octets):
        typecode = chr(octets[0])
        memv = memoryview(octets[1:]).cast(typecode)
        return cls(*memv)

    def __format__(self, format_spec=''):
        if format_spec.endswith('p'):
            format_spec = format_spec[:-1]
            coords = (abs(self), self.angle())
            outer_fmt = '<{}, {}>'
        else:
            coords = self
            outer_fmt = '({}, {})'
        components = (format(c, format_spec) for c in coords)
        return outer_fmt.format(*components)

    def angle(self):
        return math.atan2(self.y, self.x)

    def __hash__(self):
        '''Рекомендуется вычислять hash кортежа покомпонентно
            ИЛИ
           Объединить хеши атрибутов экземпляра с помощью оператора ИСКЛЮЧАЮЩЕЕ ИЛИ (XOR)'''

        return hash(tuple(self))
        #return (hash(self.x) ^ hash(self.y))

# Декораторы classmethod и staticmethod
'''
Декоратор classmethod изменяет способ вызова метода таким образом, что в качестве первого аргумента передается сам класс, а не экземпляр.

Декоратор staticmethod изменяет метод так, что он не получает в первом аргументе ничего специального.
По существу, статический метод - это просто обычная функция, определенная в теле класса, а не на уровне модуля.
'''

# Сравнение декораторов classmethod и staticmethod
class Demo:
    @classmethod
    def klassmeth(*args):
        return args
    @staticmethod
    def statmeth(*args):
        return args

print(Demo.klassmeth('spam'))
print(Demo.statmeth('spam'))

# Форматирование при выводе
brl = 1 / 4.82
print(brl)
print(format(brl, '0.4f'))
print('1 BRL = {rate:0.2f}'.format(rate=brl))
print(f'1 USD = {1 / brl:0.2f} BRL')

# Поддержка позиционного сопоставления с образцом

# Сопоставление с именованными образцами
def keyword_pattern_demo(v: Vector2d) -> None:
    match v:
        case Vector2d(x=0, y=0):
            print(f'{v!r} is null')
        case Vector2d(x=0):
            print(f'{v!r} is vertical')
        case Vector2d(y=0):
            print(f'{v!r} is horizontal')
        case Vector2d(x=x, y=y) if x==y:
            print(f'{v!r} is diagonal')
        case _:
            print(f'{v!r} is awesome')

# Сравнение с позиционными образцами
def positional_pattern_demo(v: Vector2d) -> None:
    match v:
        case Vector2d(0, 0):
            print(f'{v!r} is null')
        case Vector2d(0):
            print(f'{v!r} is vertical')
        case Vector2d(_, 0):
            print(f'{v!r} is horizontal')
        case Vector2d(x, y) if x==y:
            print(f'{v!r} is diagonal')
        case _:
            print(f'{v!r} is awesome')

v = Vector2d(1, 1)
keyword_pattern_demo(v)
positional_pattern_demo(v)
print(v.__dict__)

'''
Переменные с двумя передними подчеркиваниями __var - закрытые. 
Переменные с одним передним подчеркиванием _var - 'защищенные'. Это просто соглашение, для интерпитатора это ничего не значит.
'''

# Экономи памяти с помощью атрибута класса __slots__
'''
По умолчанию Python хранит атрибуты экземпляра в словаре __dict__, принадлежащем самому экземпляру. 
__dict__ влечет за собой значительные накладные расходы.
Но если определить атрибут класса __slots__, в котором хранится последовательность имен атрибутов, то Python будет
использовать альтернативную модель хранения для атрибутов экземпляра:
атрибуты с именами, представленными в __slots__, хранятся в скрытом массиве ссылок, потребляющем намного меньше памяти, чем __dict__.
'''
class Pixel:
    '''__slots__ должен присутствовать в момент создания класса;
        добавление или изменение вполследствии не оказывает никакого эффекта.
        Имена атрибутов могут храниться в кортеже или в списке, но лучше использовать кортеж,
        чтобы сразу было понятно, что изменять его нет никакого смысла.

        Используя __slots__ код работает быстрее и потребляет памяти примерно в 3 раза меньше, чем с __dict__.'''
    __slots__ = ('x', 'y')

p = Pixel()
p.x = 10
p.y = 20
#p.color = 'red'

class openPixel(Pixel):
    __slots__ = ('color', '__dict__')

op = openPixel()
op.x = 5
op.color = 'red'
op.flavor = 'banana'
print(op.__dict__)

# Проблемы при использовании __slots__
'''
Атрибут __slots__ при правильном использовании может дать значительную экономию памяти, но есть несколько подводных камней.
> Не забывайте заново объявлять __slots__ в каждом подклассе, потому что унаследованный атрибут интерпретатор игнорирует;
> Экземпляры класса могут иметь только атрибуты, явно перечисленные в __slots__, если в него не включено также имя __dict__ 
(однако при этом вся экономия памяти может быть сведена на нет)
> Для классов, где используется __slots__, нельзя употреблять декоратор @cached_property, если только 
в __slots__ явно не включено имя __dict__.
> Экземпляры класса не могут быть объектами слабых ссылок, если не включить в __slots__ имя __weakref__.
'''

# Переопределение атрибутов класса
v = Vector2d(1.1, 2.2)
b = bytes(v)
print(b)
v.typecode = 'f'
b = bytes(v)
print(b)

class shortVector2d(Vector2d):
    typecode = 'f'

sv = shortVector2d(1/11, 1/27)
print(sv)
print(bytes(sv))
print(hash(sv))