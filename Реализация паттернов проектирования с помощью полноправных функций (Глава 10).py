# Классическая Стратегия
'''
Определить семейство алгоритмов, инкапсулировать каждый из них и сделать их взаимозаменяемыми.
Стратегия позволяет заменять алгоритм независимо от использующих его клиентов.
'''

'''
Наглядный пример применения паттерна Стратегия в коммерческой задаче - вычисление скидок на заказы в соответствии
с характеристиками заказчика или результатами анализа заказанных позиций.

Рассмотрим интернет-магазин со следующими правилами формирования скидок:
> заказчику, имеющему не менее 1000 баллов лояльности, предоставляется глобальная скидка 5% на весь заказ;
> на позиции, заказанные в колиестве не менее 20 единиц в одном заказе, предоставляется скидка 10%;
> на заказы, содержащие не менее 10 различных позиций, предоставляется глобальная скидка 7%.

Предположим, что для каждого заказа может быть применена только одна скидка.

Участниками паттерна Стратегия являются:
> Контекст:
Предоставляет службу, делигируя часть вычислений взаимозаменяемым компонентам, реализующим различные алгоритмы.
В примере интернет-магазина контекстом является класс Order, который конфигурируется для применения
поощрительной скидки по одному из нескольких алгоритмов.

> Стратегия:
Интерфейс, общий для всех компонентов, реализующих различные алгоритмы.
В нашем примере эту роль играет абстрактный класс Promotion.

> Конкретная стратегия:
Один из конкретных подклассов Стратегии. В нашем случае реализованы три конкретные стратегии:
FidelityPromo, BulkPromo, LargeOrderPromo.
'''

from abc import ABC, abstractmethod
from collections.abc import Sequence
from decimal import Decimal
from typing import NamedTuple, Optional

class Customer(NamedTuple):
    name: str
    fidelity: int

class LineItem(NamedTuple):
    product: str
    quantity: int
    price: Decimal

    def total(self) -> Decimal:
        return self.price * self.quantity

class Order(NamedTuple): # Контекст
    customer: Customer
    cart: Sequence[LineItem]
    promotion: Optional['Promotion'] = None

    def total(self) -> Decimal:
        totals = (item.total() for item in self.cart)
        return sum(totals, start=Decimal(0))

    def due(self) -> Decimal:
        if self.promotion is None:
            discount = Decimal(0)
        else:
            discount = self.promotion.discount(self)
        return self.total() - discount

    def __repr__(self):
        return f'<Order total: {self.total():.2f} due: {self.due():.2f}>'

class Promotion(ABC): # Абстрактный базовый класс
    @abstractmethod
    def discount(self, order: Order) -> Decimal:
        '''Вернуть скидку в виде положительной суммы в долларах'''

class FidelityPromo(Promotion): # Первая конкретная стратегия
    '''5%-ная скидка для заказчиков, имеющих не менее 1000 баллов лояльности'''

    def discount(self, order: Order) -> Decimal:
        rate = Decimal('0.05')
        if order.customer.fidelity >= 1000:
            return order.total() * rate
        return Decimal(0)

class BulkItemPromo(Promotion): # Вторая конкретная стратегия
    '''10%-ная скидка для каждой позиции LineItem, в которой заказано не менее 20 единиц'''

    def discount(self, order: Order) -> Decimal:
        discount = Decimal(0)
        for item in order.cart:
            if item.quantity >= 20:
                discount += item.total() * Decimal('0.1')
            return discount

class LargeOrderPromo(Promotion): # Третья конкретная стратегия
    '''7%-ная скидка для заказов, включающих не менее 10 различных позиций'''

    def discount(self, order: Order) -> Decimal:
        distinct_items = {item.product for item in order.cart}
        if len(distinct_items) >= 10:
            return order.total() * Decimal('0.07')
        return Decimal(0)

joe = Customer('John Doe', 0)
ann = Customer('Ann Smith', 1100)
cart = (LineItem('banana', 4, Decimal('.5')),
        LineItem('apple', 10, Decimal('1.5')),
        LineItem('watermelon', 5, Decimal(5)))
print(Order(joe, cart, FidelityPromo()))
print(Order(ann, cart, FidelityPromo()))
banana_cart = (LineItem('banana', 30, Decimal('.5')),
               LineItem('apple', 10, Decimal('1.5')))
print(Order(joe, banana_cart, BulkItemPromo()))
long_cart = tuple(LineItem(str(sku), 1, Decimal(1)) for sku in range(10))
print(Order(joe, long_cart, LargeOrderPromo()))

# Функционально-ориентированная Стратегия

from collections.abc import Sequence, Callable
from typing import NamedTuple, Optional
from decimal import Decimal

class Customer(NamedTuple):
    name: str
    fidelity: int

class LineItem(NamedTuple):
    product: str
    quantity: int
    price: Decimal

    def total(self) -> Decimal:
        return self.price * self.quantity

class Order(NamedTuple): # Контекст
    customer: Customer
    cart: Sequence[LineItem]
    promotion: Optional[Callable[['Order'], Decimal]] = None

    def total(self) -> Decimal:
        totals = (item.total() for item in self.cart)
        return sum(totals, start=Decimal(0))

    def due(self) -> Decimal:
        if self.promotion is None:
            discount = Decimal(0)
        else:
            discount = self.promotion(self)
        return self.total() - discount

    def __repr__(self):
        return f'<Order total: {self.total():.2f} due: {self.due():.2f}>'

def fidelity_promo(order: Order) -> Decimal:
    '''5%-ная скидка для заказчиков, имеющих не менее 1000 баллов лояльности'''
    if order.customer.fidelity >= 1000:
        return order.total() * Decimal('0.05')
    return Decimal(0)

def bulk_item_promo(order: Order) -> Decimal:
    '''10%-ная скидка для каждой позиции LineItem, в которой заказано не менее 20 единиц'''
    discount = Decimal(0)
    for item in order.cart:
        if item.quantity >= 20:
            discount += item.total() * Decimal('0.1')
        return discount

def large_order_promo(order: Order) -> Decimal:
    """7%-ная скидка для заказов, включающих не менее 10 различных позиций"""
    distinct_items = {item.product for item in order.cart}
    if len(distinct_items) >= 10:
        return order.total() * Decimal('0.07')
    return Decimal(0)

joe = Customer('John Doe', 0)
ann = Customer('Ann Smith', 1100)
cart = (LineItem('banana', 4, Decimal('.5')),
        LineItem('apple', 10, Decimal('1.5')),
        LineItem('watermelon', 5, Decimal(5)))
print(Order(joe, cart, fidelity_promo))
print(Order(ann, cart, fidelity_promo))
banana_cart = (LineItem('banana', 30, Decimal('.5')),
               LineItem('apple', 10, Decimal('1.5')))
print(Order(joe, banana_cart, bulk_item_promo))
long_cart = tuple(LineItem(str(sku), 1, Decimal(1)) for sku in range(10))
print(Order(joe, long_cart, large_order_promo))

# Выбор наилучшей стратегии: простой подход
promos = [fidelity_promo,
          bulk_item_promo,
          large_order_promo
]

def best_promo(order: Order) -> Decimal:
    '''Вычислить наибольшую скидку'''
    return max(promo(order) for promo in promos)

print()
print(Order(joe, long_cart, best_promo))
print(Order(joe, banana_cart, best_promo))
print(Order(ann, cart, best_promo))

# Поиск стратегий в модуле
# Список promos строится путем просмотра глобального пространства имен модуля
promos = [promo for name, promo in globals().items() if name.endswith('_promo') and name != 'best_promo']
print(promos)

# Паттерн Стратегия, дополненный декоратором
from typing import TypeAlias

Promotion: TypeAlias = Callable[[Order], Decimal]
promos: list[Promotion] = []

def promotion(promo: Promotion) -> Promotion:
    promos.append(promo)
    return promo

def best_promo(order: Order) -> Decimal:
    '''Вычислить наибольшую скидку'''
    return max(promo(order) for promo in promos)

@promotion
def fidelity(order: Order) -> Decimal:
    '''5%-ная скидка для заказчиков, имеющих не менее 1000 баллов лояльности'''
    if order.customer.fidelity >= 1000:
        return order.total() * Decimal('0.05')
    return Decimal(0)

@promotion
def bulk_item(order: Order) -> Decimal:
    '''10%-ная скидка для каждой позиции LineItem, в которой заказано не менее 20 единиц'''
    discount = Decimal(0)
    for item in order.cart:
        if item.quantity >= 20:
            discount += item.total() * Decimal('0.1')
        return discount

@promotion
def large_order(order: Order) -> Decimal:
    '''10%-ная скидка для каждой позиции LineItem, в которой заказано не менее 20 единиц'''
    discount = Decimal(0)
    for item in order.cart:
        if item.quantity >= 20:
            discount += item.total() * Decimal('0.1')
        return discount

print(promos)

# Паттерн Команда
class MacroCommand:
    '''Команда, выполняющая список команд'''

    def __init__(self, commands):
        self.commands = list(commands)

    def __call__(self):
        for command in self.commands:
            command()
