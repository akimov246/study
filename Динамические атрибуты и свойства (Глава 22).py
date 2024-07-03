'''
Атрибуты-данные и методы в Python носят общее название "атрибуты";
метод - это просто вызываемый атрибут. Помимио атрибутов-данных и методов, мы можем создавать еще свойства, позволяющие
заменить откртые атрибуты-данные методами-акцессорами (т.е. методами чтения и установки), не изменяя интерфейс класса.
В Python есть несколько способов реализовать динамиеческие атрибуты, например декоратор @property и специальный
метод __getattr__.
Пользовательский класс, в котором имеется метод __getattr__, может реализовать вариант динамиечких атрибутов, называемый
виртуальными атрибутами; они не объявлены в исходном коде класса и отсутствуют в экземпляре __dict__, но могут быть получены
из какого-то другого места или вычислены "на лету", когда программа пытается прочитать несуществующий атрибут,
например obj.no_such_attr.
Динамические атрибуты - вид метапрограммирования, обычно применяемый авторами каркасов. Однако в Python базовая техника
настолько проста, что любой человек может воспользоваться ими, даже для повседневных задач обработки данных.
'''

# Применение динамических атрибутов для обработки данных
import json
import keyword

with open('data/osconfeed.json') as fp:
    feed = json.load(fp) # Загрузить как слова dict, содержащий вложенные словари и списки со строковыми и целыми значениями

print(sorted(feed['Schedule'].keys())) # Вывести все четыре коллекции записей внутри 'Schedule'

for key, value in sorted(feed['Schedule'].items()):
    print(f'{len(value):>3} {key}') # Вывести счетчик записей в каждой коллекции

print(feed['Schedule']['speakers'][-1]['name']) # Обойти вложенные словари и списки, чтобы полуить имя последнего докладчика
print(feed['Schedule']['speakers'][-1]['serial']) # Получить порядковый номер этого докладчика

# Исследование JSON-подобных данных с динамическими атрибутами

# explore0.py: преобразование набора данных из формата JSON в объект FrozenJSON, содержащий вложенные объекты FrozenJSON,
# списки и значения примитивных типов

from collections import abc
class FrozenJSON:
    '''Допускающий только чтение фасад для навигации по JSON-подобному объекту с применением нотации атрибутов'''

    def __init__(self, mapping):
        self.__data = dict(mapping) # Построить объект dict по аргументу mapping. Тем самым мы проверяем, что получили
                                    # словарь (или нечто, что можно преобразовать в словарь). Два знака подчеркивания
                                    # в начале __data говорят, что это закрытый атрибут

    def __getattr__(self, name): # Метод __getattr__ вызывается, только когда не существует атрибута с именем name
        try:
            return getattr(self.__data, name) # Если имени name соответствует какой-то атрибут словаря __data,
                                              # возвращаем его. Так обрабатываются вызовы методов типа feed.keys():
                                              # метод keys является атрибутом словаря __data.
        except AttributeError:
            return FrozenJSON.build(self.__data[name]) # В противном случае получаем элемент с ключом name из self.__data
                                                       # и возвращаем результат вызова для него метода FrozenJSON.build()

    def __dir__(self):
        return self.__data.keys()

    @classmethod
    def build(cls, obj): # Это альтернативный конструктор, типичное применение декоратора @classmethod
        if isinstance(obj, abc.Mapping): # Если obj - отображение, строим по нему объект FrozenJSON. Это пример гусиной типизации
            return cls(obj)
        elif isinstance(obj, abc.MutableSequence): # Если это экземпляр MutableSequence, то он должен быть списком, поэтому
                                                   # строим список, рекурсивно передавая каждый элемент obj методу .build()
            return [cls.build(item) for item in obj]
        else:
            return obj # Если это не dict и не list, возвращаем элемент без изменения.

raw_feed = json.load(open('data/osconfeed.json'))
feed = FrozenJSON(raw_feed)
print(len(feed.Schedule.speakers))
print(feed.keys())
print(sorted(feed.Schedule.keys()))
for key, value in sorted(feed.Schedule.items()):
    print(f'{len(value):>3} {key}')
print(feed.Schedule.speakers[-1].name)

# Проблема недоступности имени атрибута
'''
У класса FrozenJSON есть ограничение: в нем не предусмотрена специальная обработка имен атрибутов, являющихся ключевыми
словами Python, например:
    student = FrozenJSON({'name': 'Jim Bo', 'class': 1982})
Мы не сможем прочитать атрибут student.class, т.к. class - зарезервированное слово в Python.
Конечно, можно сделать так:
getattr(student, 'class')
Но идея класса FrozenJSON заключалась в том, чтобы предоставить удобный доступ, поэтому лучше, является ли ключ отображения,
переданного методу FrozenJSON.__init__, зарезервированным словом, и если да, то добавлять в конец символ _, чтобы атрибут можно
было прочитать так:
student.class_
'''

# explore1.py: Добавление _ в имена атрибутов, являющихся зарезервинованными словами Python
class FrozenJSON:

    def __init__(self, mapping):
        self.__data = {}
        for key, value in mapping.items():
            if keyword.iskeyword(key):
                key += '_'
            self.__data[key] = value

    def __getattr__(self, name):
        try:
            return getattr(self.__data, name)
        except AttributeError:
            return self.build(self.__data[name])

    @classmethod
    def build(cls, obj):
        if isinstance(obj, abc.Mapping):
            return cls(obj)
        elif isinstance(obj, abc.MutableSequence):
            return [cls.build(item) for item in obj]
        else:
            return obj

# Гибкое создание объектов с помощью метода __new__
'''
В Python метод __init__ получает self в качестве первого аргумента, поэтому к моменту вызова __init__ интерпретатором
объект уже существует. Кроме того, __init__ не может ничего возвращать. Так что в действительности это инициатор, а не конструктор.
Когда класс вызывается для создания экземпляра, Python вызывает специальный метод класса __new__. Хотя это метод класса,
обрабатывается он не так, как другие: к нему не применяется декоратор @classmethod. Python принимает экземпляр,
возвращенный __new__, и передает его в качестве первого аргумента self методу __init__. Мы редко пишем __new__ самостоятельно,
потому что реализации, унаследованной от object, обычно достаточно.
При необходимости метод __new__ может вернуть экземпляр друго класса. В таком случае интерпретатор не вызывает __init__.
Иными словами, логика создания объекта в Python описывается следующим псевдокодом:
    def make(the_class, some_arg):
        new_object = the_class.__new__(some_arg)
        if isinstance(new_object, the_class):
            the_class.__init__(new_object, some_arg)
        return new_object
'''

# explore2.py: использования __new__ вместо build для конструирования новых объектов, которые могут быть или не быть
# экхемплярами FrozenJSON

from collections import abc
import keyword

class FrozenJSON:

    def __new__(cls, arg): # Будучи методом класса, __new__ получает в качестве первого аргумента сам класс, а остальные
                           # аргументы - те же, что получает __init__, за исключением self.
        if isinstance(arg, abc.Mapping):
            return super().__new__(cls) # По умолчаню работа делигируется методу __new__ суперкласса. В данном случае
                                        # мы вызываем метод __new__ из базового класса object, передавая ему FrozenJSON
                                        # в качестве единственного аргумента.
        elif isinstance(arg, abc.MutableSequence):
            return [cls(item) for item in arg]
        else:
            return arg

    def __init__(self, mapping):
        self.__data = {}
        for key, value in mapping.items():
            if keyword.iskeyword(key):
                key += '_'
            self.__data[key] = value

    def __getattr__(self, name):
        try:
            return getattr(self.__data, name)
        except AttributeError:
            return FrozenJSON(self.__data[name]) # Здесь раньше вызывался метод FrozenJSON.build, а теперь мы просто вызываем
                                                 # класс FrozenJSON, а Python обрабатывает это как вызов FrozenJSON.__new__.

'''
Метод __new__ получает в качестве первого аргумента класс, потому что обычно создается экземпляр именно этого класса.
Таким образом, при вызове super().__new__(cls) из FrozenJSON.__new__ в действительности вызывается object.__new__(FrozenJSON),
а объект, построенный классом object, является экземпляром класса FrozenJSON.
'''

# Вычисляемые свойства
# Шаг 1: создание управляемого данными атрибута
import json
import inspect

JSON_PATH = 'example-code-2e/22-dyn-attr-prop/oscon/data/osconfeed.json'

class Record:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs) # Стандартная идиома для построения экземпляра, атрибуты которого создаются
                                     # из именованных аргументов

    def __repr__(self):
        return f'<{self.__class__.__name__} serial={self.serial!r}>' # Использовать поле serial, чтобы построить представление Record

    def load(path=JSON_PATH):
        records = {} # Метод load в конечном итоге вернет словарь экземпляров Record.
        with open(path) as fp:
            raw_data = json.load(fp) # Разобрать JSON и вернуть объекты Python: списки, словари, числа и т.д.
        for collection, raw_records in raw_data['Schedule'].items(): # Обойти все четыре списка верхнего уровня:
                                                                     # 'conferences', 'events', 'speakers' и 'venues'
            record_type = collection[:-1] # record_type - имя списка без последнего символа, т.е. speakers становится speaker.
            for raw_record in raw_records:
                key = f'{record_type}.{raw_record["serial"]}' # Построить ключ в формате 'speaker.3471'
                records[key] = Record(**raw_record) # Создать экземпляр Record и сохранить его в словаре records под ключем key.
        return records

'''
В методе Record.__init__ иллюстрируется распространенный при программировании на Python прием. В словаре __dict__ объекта
хранятся атрибуты - если только в классе не объявлен атрибут __slots__. Поэтому копирование в __dict__ отображения - быстрый
способ сразу несколько атрибутов экземпляра.
'''

recors = Record.load(JSON_PATH)
speaker = recors['speaker.3471']
print(speaker)

# Шаг 2: выборка связанных записей с помощью свойств
class Record:

    __index = None # В закрытом атрибуте класса __index будет храниться ссылка на dict, возвращенный методом load()

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def __repr__(self):
        return f'<{self.__class__.__name__} serial={self.serial!r}>'

    @staticmethod # fetch сделан статическим методом, чтобы было понятно, что его действие не зависит от экземпляра или класса,
                  # от имено которого он вызывается
    def fetch(key):
        if Record.__index is None: # Заполнить Record.__index если необходимо
            Record.__index = load()
        return Record.__index[key] # Нужно, чтобы извлечь запись с заданным ключем key

class Event(Record): # Класс Event расширяет Record

    def __repr__(self):
        try:
            return f'<{self.__class__.__name__} {self.name!r}>' # Если в экземпляре есть атрибут name, включаем его в
                                                                # строковое представление. В противном случае делегируем
                                                                # методу __repr__, унаследованному от Record.
        except AttributeError:
            return super().__repr__()

    @property
    def venue(self):
        key = f'venue.{self.venue_serial}'
        return self.__class__.fetch(key) # Свойство venue строит ключ key по атрибуту venue_serial и передает его методу
                                         # класса fetch, унаследованному от Record

    # Шаг 3: Переопределение существующего атрибута свойством
    @property
    def speakers(self):
        spkr_serials = self.__dict__['speakers'] # Нужные нам данные находятся в атрибуте speakers, но получить их мы
                                                 # должны непосредственно из экземпляра __dict__, чтобы избежать рекурсивного
                                                 # обращения к свойству speakers.
        fetch = self.__class__.fetch
        return [fetch(f'speaker.{key}') for key in spkr_serials] # Вернуть список всех записей с ключами, соответствующими
                                                                 # числам в spkr_serials.

def load(path=JSON_PATH):
    records = {}
    with open(path) as fp:
        raw_data = json.load(fp)
    for collection, raw_records in raw_data['Schedule'].items():
        record_type = collection[:-1]
        cls_name = record_type.capitalize() # Преобразовать первую буквы record_type в верхний регистр, чтобы получить
                                            # потенциальное имя класса.
        cls = globals().get(cls_name, Record) # Получить объект с таким именем из глобальной области видимости модуля;
                                              # если такого объекта нет, получаем Record
        if inspect.isclass(cls) and issubclass(cls, Record): # Если только что полученный объект - класс, который является
                                                             # подклассом Record, то...
            factory = cls # Связывать с ним имя factory. Это означает, что factory может быть произвольным подклассом Record,
                          # определяемым переменной record_type
        else:
            factory = Record # В противном случае связать имя factory с Record.
        for raw_record in raw_records: # Цикл for, в котором создаются ключи и сохраняются записи, такой же, как и раньше,
                                       # с тем исключение, что ...
            key = f'{record_type}.{raw_record["serial"]}'
            records[key] = factory(**raw_record) # ... объект, сохраняемый в records, конструируется функцией factory,
                                                 # которая может быть конструктором Record или его подкласса - в зависимости
                                                 # от значения record_type
        return records

'''
При вычислении obj.my_attr интерпретатор сначала смотрит на класс obj. Если в классе имеется свойство с именем my_attr, 
то оно маскирует одноименный атрибут экземпляра. 
'''

# Дескриптор - это объект, который управляет доступом к атрибуту в другом классе.

'''
Декоратор @functools.cached_property кеширует результат метода в одноименном атрибуте результата. 
Механизмы работы cached_property() и property() различаются. Обычное свойство запрещает запись в атрибут, если не определен
метод установки. А cached_property разрешает запись всегда.
Декоратор cached_property работает только в момент проверки существования и только при условии, что атрибута с таким же 
именем не существует.
В этом случае cached_property записывает в атрибут с таким же именем. Последующие операции чтения и записи имеют более
высокий приоретет, чем метод cached_property, поэтому кешированное свойство работает, как обычный атрибут.
Кешированное значение можно очистить, удалив атрибут. После этого метод cached_property будет работать снова.

Декоратор @cached_property имеет несколько важных ограничений:
> Его нельзя использовать в качестве замены @property, если декорируемый метод уже зависит от существования одноменного 
атрибута экземпляра;
> Его нельзя использовать в классе, где определен атрибут __slots__;
> Он подавляет оптимизацию разделения ключей в экземпляре __dict__, потому что создает атрибут экземпляра после __init__.
'''

# Использование свойств для контроля атрибутов
'''
Помимо вычисления значений атрибутов, свойства применяются с целью реализации бизнес-правил. Для этого открытый атрибут 
заменяется атрибутом, защищенным методами чтения и установки, без изменения клиентского кода.
'''

# LineItem, попытка №1: класс строки заказа
'''
Представим себе приложение для магазина, который продает натуральные пищевые продукты вразвес, т.е. клиенты могут
заказать орехи, сухофрукты или хлопья по весу. В такой системе заказ состоит из последовательности строк, а каждую
строку можно представить классом.
'''

class LineItem:

    def __init__(self, description, weight, price):
        self.description = description
        self.weight = weight
        self.price = price

    def subtotal(self):
        return self.weight * self.price

raisins = LineItem('Golden raisins', 10, 6.95)
print(raisins.subtotal())
raisins.weight = -20 # мусор на входе
print(raisins.subtotal()) # мусор на выходе

'''
Красиво и просто, но если ввести, например, значение weight отрицательно число, то мы получим непредполагаемые значения
на выходе.
Как это исправить? Можно было бы изменить интерфейс класса LineItem, добавив методы чтения и установки атрибута weight.
С другой стороны, было бы естественно устанавливать атрибут weight элемента заказа, просто присваивая ему значение, 
да и не исключено, что в других частях эксплуатируемой системы уже встречается прямой доступ к атрибуту self.weight.
В таком случае следовало бы заменить атрибут-данные свойством - это было бы в духе Python.
'''

# LineItem, попытка №2: контролирующее свойство
'''
Реализовав свойство, мы сможем использовать методы чтения и установки, но интерфейс класс LineItem при этом не изменится 
(т.е. для установки атрибута weight объекта LineItem по-прежнему нужно будет написать obj.weight = 12)
'''

class LineItem:

    def __init__(self, description, weight, price):
        self.description = description
        self.weight = weight # Здесь уже используется метод установки свойства, который гарантирует, что не может быть
                             # создан экземпляр с отрицательным значением weight.
        self.price = price

    def subtotal(self):
        return self.weight * self.price

    @property # Декоратором @property обозначается метод чтения свойства.
    def weight(self): # Имена всех методов, реализующих свойство, совпадают с именем открытого атрибута: weight
        return self.__weight # Фактическое значение хранится в закрытом атрибуте __weight

    @weight.setter # У декорированного метода чтения свойства имеется атрибут .setter, который является также и декоратором;
                   # тем самым метод чтения и установки связываются между собой
    def weight(self, value):
        if value > 0:
            self.__weight = value # Если значение больше нуля, присваиваем его закрытому атрибуту __weight
        else:
            raise ValueError('value must be > 0') # В противном случае возбуждаем исключение ValueError

# Теперь объект LineItem с недопустимым весом создать невозможно:
# walnuts = LineItem('walnuts', 0, 10.00)

'''
Итак, мы защитили атрибут weight от присваивания отрицательных значений пользователем. Но хотя покупатели обычно не в праве
устанавливать цену товара, в результате ошибки служащего или программы все же можеть быть создан объект LineItem с 
отрицательной ценой price. Чтобы предотвратить и это, мы могли бы преобразовать price в свойство, но это повлекло бы 
за собой частичное повторение кода.
Лекарство от повторения - абстрагирование. Существует два способа абстрагировать определения свойств: 
фабрика свойств и дескрипторный класс.
'''

# Атрибут экземпляра маскирует атрибут-данные класса
class Class: # Определить Class с двумя атрибутами класса: атрибутом-данными data и свойством prop
    data = 'the class data attr'

    @property
    def prop(self):
        return 'the prop value'

obj = Class()
print(vars(obj)) # vars возвращает атрибут __dict__ объекта obj; как видим, атрибутов экземпляра в нем нет
print(obj.data) # Чтение из obj.data возвращает значение Class.data
obj.data = 'bar' # Запись в obj.data создает атрибут экземпляра
print(vars(obj)) # Проинспектировать экземпляр, чтобы узнать, какие у него атрибуты
print(obj.data) # Теперь, читая obj.data, мы получаем значение атрибута экземпляра. При чтении из экземпляра obj атрибут
                # экземпляра data маскирует атрибут класса data
print(Class.data) # Атрибут Class.data не изменился
# Попробуем теперь переопределить атрибут prop экземпляра obj
print(Class.prop) # Чтение prop непосредственно из Class возвращает сам объект свойства, при этом метод чтения не выполняется
print(obj.prop) # Чтение obj.prop приводит к выполнению метода чтения
#obj.prop = 'foo' # Попытка установить атрибут экземпляра prop завершается ошибкой
obj.__dict__['prop'] = 'foo' # Запись 'prop' напрямую в __dict__ работает
print(vars(obj)) # Как видим, теперь у obj есть два атрибута экземпляра: data и prop
print(obj.prop) # Однако при чтении obj.prop по-прежнему выполняется метод чтения свойства. Свойство не маскируется атрибутом экземпляра
Class.prop = 'baz' # В случае перезаписывания Class.prop объект свойства уничтожается
print(obj.prop) # Теперь чтение obj.prop возвращает атрибут экземпляра. Class.prop больше не является свойством, поэтому
                # и не переопределяет obj.prop
# В качестве заключительно демонстрации добавим новое свойство в Class и убедимся, что оно переопределяет атрибут экземпляра.
print(obj.data) # obj.data возвращает атрибут экземпляра data
print(Class.data) # Class.data возвращает атрибут класса data
Class.data = property(lambda self: 'the "data" prop value') # Перезаписать Class.data новым свойством
print(obj.data) # Теперь Class.data маскирует obj.data
del Class.data # Удалить свойство
print(obj.data) # Теперь obj.data снова возвращает атрибут экземпляра data
'''
При вычислении выражения вида obj.data поиск data начинаается не с obj. На самом деле поиск начинается с obj.__class__, 
и только если в классе не существует свойства с именем data, то Python заглядывает в сам объект obj.
'''

# Документирование свойств
class Foo:

    @property
    def bar(self):
        '''Атрибут bar'''
        return self.__dict__['bar']

    @bar.setter
    def bar(self, value):
        self.__dict__['bar'] = value

help(Foo.bar)
print(Foo.bar.__doc__)

# Программирование фабрики свойств