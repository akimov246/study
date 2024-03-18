# Функция super()

import collections

class LastUpdatedOrderedDict(collections.OrderedDict):
    '''Элементы хранятся в порядке, определенном последним обновлением'''
    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        self.move_to_end(key)

# Сложности наследования встроенным типам
'''
Вместо создания подклассов встроенных объектов наследуйте свои классы от классов в модуле collections -
UserDict, UserList, UserString, которые специально предназначены для беспроблемного наследования.
'''

class DopplerDict(dict):
    def __setitem__(self, key, value):
        super().__setitem__(key, [value] * 2)

dd = DopplerDict(one=1)
dd['two'] = 2
dd.update(thre=3)
print(dd)

class DopplerDict2(collections.UserDict):
    def __setitem__(self, key, value):
        super().__setitem__(key, [value] * 2)

dd2 = DopplerDict2(one=1)
dd2['two'] = 2
dd2.update(three=3)
print(dd2)

# Множественное наследование и порядок разрешения методов

class Root:
    def ping(self):
        print(f'{self}.ping() in Root')

    def pong(self):
        print(f'{self}.pong() in Root')

    def __repr__(self):
        cls_name = type(self).__name__
        return f'<instance of {cls_name}>'

class A(Root):
    def ping(self):
        print(f'{self}.ping() in A')
        super().ping()

    def pong(self):
        print(f'{self}.pong() in A')
        super().pong()

class B(Root):
    def ping(self):
        print(f'{self}.ping() in B')
        super().ping()

    def pong(self):
        print(f'{self}.pong() in B')

class Leaf(A, B):
    def ping(self):
        print(f'{self}.ping() in Leaf')
        super().ping()

leaf1 = Leaf()
leaf1.ping()
leaf1.pong()
print(Leaf.__mro__)

# Классы-примеси
'''
Класс-примесь - класс, который предназначен для работы с другими классами при множественном наследовании
с целью придать им дополнительную функциональность.
'''

# Отображения, не зависящие от регистра

def _upper(key):
    try:
        return key.upper()
    except AttributeError:
        return key

class UpperCaseMixin: # Класс-примесь
    '''Класс, который дает не зависящий от регистра доступ к отображениям с ключами-строками'''

    def __setitem__(self, key, item):
        super().__setitem__(_upper(key), item)

    def __getitem__(self, key):
        return super().__getitem__(_upper(key))

    def get(self, key, default=None):
        return super().get(_upper(key), default)

    def __contains__(self, key):
        return super().__contains__(_upper(key))

'''
Поскольку все методы UpperCaseMixin вызывает super(), эта примесь зависит от класса на том же уровне иерархии,
который реализует или наследует методы с такой же сигнатурой. Чтобы внести свой вклад, примесь обычно должна
находиться раньше других классов в MRO использующего ее подкласса. На практике это означает, что примеси 
должны располгааться в начале кортежа базовых классов в объявлении класса.
'''

class UpperDict(UpperCaseMixin, collections.UserDict):
    '''Специализированный Dict, который переводит строковые ключи в верхний регистр'''

class UpperCounter(UpperCaseMixin, collections.Counter):
    '''Специализированный Counter, который переводит строковые ключи в верхний регистр'''

d = UpperDict([('a', 'letter A'), (2, 'digit two')])
print(list(d.keys()))
d['b'] = 'letter B'
print('b' in d)
print(d['a'], d.get('B'))
print(list(d))

c = UpperCounter('BaNanA')
print(c.most_common())

print(UpperDict.__mro__)


