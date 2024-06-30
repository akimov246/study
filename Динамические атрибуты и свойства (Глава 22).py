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