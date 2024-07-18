'''
Дескрипторы - это способ повторного использования одной и той же логики доступа в нескольких атрибутах.
Дескрипторы - это класс, который реализует динамический протокол, содержащий методы __get__, __set__ и __delete__.
Класс property реализует весь протокол дескриптора. Как обычно, разрешается реализовывать протокол частично.
На самом деле большинство дескрипторов, встречающихся в реальных программах, реализуют только методы __get__ и __set__,
а многие - и вовсе лишь один из них.
'''

# Пример дескриптора: проверка значений атрибутов
'''
Фабрика свойств - это функция высшего порядка, которая создает параметризованный набор функций-акцессоров и строит их них
экземпляры пользовательских свойств, настройки которых, например storage_name, хранятся в замыканиях. Объектно-ориентированный
способ решения этой задачи - дескрипторный класс.

Дескрипторный класс - класс, реализующий протокол дескриптора (__get__ or(and) __set__ or(and) __delete__);

Управляемый класс - класс в котором объявлены атрибуты класса, являющиеся экземплярами дескриптора;

Экземпляр дескриптора - любой экземпляр дескрипторного класса, объявленный атрибутом в управляемом классе;

Управляемый экземпляр - один экземпляр управляемого класса;

Атрибут хранения - атрибут управляемого экземпляра, в котором хранится значение управляемого атрибута для данного экземпляра.

Управляемый атрибут - открытый атрибут управляемого класса, который обрабатывается экземпляром дескриптора, а значение
которого хранится в одном из атрибутов хранения.
'''
# LineItem попытка №3: простой дескриптор

class Quantity: # Дескриптор основан на протоколе, для его реализации не требуется наследование

    def __init__(self, storage_name):
        self.storage_name = storage_name # В каждом экземпляре Quantity имеется атрибут storage_name: имя атрибута
                                         # хранения, в котором хранится значение управляемого экземпляра

    def __set__(self, instance, value): # Метод __set__ вызывается при любой попытке присвоить значение управляемому атрибуту.
                                        # В данном случае self - экземпляр дескриптора (т.е LineItem.weight или LineItem.price),
                                        # instance - управляемый экземпляр (экземпляр LineItem), а value - присваиваемое значение.
        if value > 0:
            instance.__dict__[self.storage_name] = value # Мы должны сохранить значение атрибута непосредственно в __dict__;
                                                         # попытка вызвать setattr(instance, self.storage_name) привела бы
                                                         # к повторному вызову метода __set__ и, стало быть, к бесконечной рекурсии.
        else:
            msg = f'{self.storage_name} must be > 0'
            raise ValueError(msg)

    def __get__(self, instance, owner): # Релизовать __get__ необходимо, потому что имя управляемого атрибута может не совпадать
                                        # с storage_name.
        return instance.__dict__[self.storage_name]

# Реализация __get__ требуется, потому что пользователь мог бы написать что-то вроде:
class House:
    rooms = Quantity('number_of_rooms')
'''
В классе House управляемым атрибутом является rooms, а атрибутом хранения number_of_rooms. Если имеется экземпляр House
с именем chaos_manor, то чтение и запись chaos_manor.rooms проходят через дескриптор Quantity, присоединенный к rooms, но
при чтении и записи chaos_manor.number_of_rooms дескриптор обходится.
Отметим, что __get__ получает три аргумента: self, instance и owner. Аргумент owner - это ссылка на управляемый класс
(например, LineItem), он полезен, если мы хотим, чтобы дескриптор поддерживал получение атрибута класса - быть может,
чтобы эмулировать поведение Python по умолчанию - извлекать атрибут класса, если указанного имени нет среди атрибутов экземпляра.
Если управляемый атрибут, например weight, запрашивается через класс - LineItem.weight, - то метод __get__ дескриптора получает
None в качестве значения аргумента instance. 
Для поддержки интроспекции и других приемов метапрограммирования пользователем рекомендуется возвращать из __get__ экземпляр
дескриптора, если доступ к управляемому атрибуту производится через класс. Для этого код __get__ следовало бы написать так:
'''
def __get__(self, instance, owner):
    if instance is None:
        return self
    else:
        return instance.__dict__[self.storage_name]


class LineItem:
    weight = Quantity('weight') # Первый экземпляр дескриптора связывается с атрибутом weight
    price = Quantity('price') # Второй экземпляр дескриптора связывается с атрибутом price

    def __init__(self, description, weight, price):
        self.description = description
        self.weight = weight
        self.price = price
        self.weight_1 = 5

    def subtotal(self):
        return self.weight * self.price

# LineItem попытка №4: автоматическое генерирование имен атрибутов хранения
'''
Чтобы не набирать повторно имя атрибута в объявлении дескриптора, мы реализуем специальный метод __set_name__, который будет 
устанавливать атрибут storage_name в каждом экземпляре Quantity. 
'''

class Quantity:

    def __set_name__(self, owner, name): # self - экземпляр дескриптора, owner - управляемый класс, а name - имя атрибута owner,
                                         # которому был назначен этот дескриптор в теле класса owner.
        self.storage_name = name # Это то, что делал __init__ в предыдущем примере

    def __set__(self, instance, value):
        if value > 0:
            instance.__dict__[self.storage_name] = value
        else:
            msg = f'{self.storage_name} must be > 0'
            raise ValueError(msg)

    # Реализовывать __get__ необязательно, потому что имя атрибута хранения совпадает с именем управляемого атрибута.
    # Выражение product.price получает атрибут price непосредственно из экземпляра LineItem.

class LineItem:
    weight = Quantity() # Теперь нам не нужно передавать имя управляемого атрибута конструктору Quantity.
    price = Quantity()

    def __init__(self, description, weight, price):
        self.description = description
        self.weight = weight
        self.price = price

    def subtotal(self):
        return self.weight * self.price

# LineItem попытка №5: новый тип дескриптора

import abc

class Validated(abc.ABC):

    def __set_name__(self, owner, name):
        self.storage_name = name

    def __set__(self, instance, value):
        value = self.validate(self.storage_name, value) # Метод __set__ делигирует проверку методу validate...
        instance.__dict__[self.storage_name] = value # ... а затем использует возвращенное значение value, чтобы обновить
                                                     # хранимое значение.

    @abc.abstractmethod
    def validate(self, name, value): # Метод validate абстрактный, это шаблонный метод.
        '''Вернуть проверенное значение или возбудить ValueError'''

class Quantity(Validated):
    '''Число, большее нуля'''

    def validate(self, name, value): # Реализация шаблонного метода, который требует абстрактный метод Validated.validate
        if value <= 0:
            raise ValueError(f'{name} must be > 0')
        return value

class NonBlank(Validated):
    '''Строка, содержащая хотя бы один символ, отличный от пробела'''

    def validate(self, name, value):
        value = value.strip()
        if not value: # Если после удаления начальных и коненых пробелов ничего не остало, то отвергнуть значение
            raise ValueError(f'{name} cannot be blank')
        return value # Требуя, чтобы конкретные методы validate возвращали проверенное значение, мы оставляем им
                     # возможность очистить, преобразовать или нормализовать полученные данные. В данном случае
                     # значение value перед возвратом очищается от начальных и конечных пробелов.

class LineItem:
    description = NonBlank()
    weight = Quantity()
    price = Quantity()

    def __init__(self, description, weight, price):
        self.description = description
        self.weight = weight
        self.price = price

    def subtotal(self):
        return self.weight * self.price

# Переопределяющие и непереопределяющие дескрипторы
