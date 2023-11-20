# Обзор построителей классов данных

class Coordinate:
    def __init__(self, lat, lon):
        self.lat = lat
        self.lon = lon

    def __eq__(self, other):
        return self.lat == other.lat and self.lon == other.lon

    def __str__(self):
        x = ", ".join([f"{key}={value}" for key, value in vars(self).items()])
        return f"{self.__class__.__name__}({x})"

moscow = Coordinate(14.88, 3.22)
print(moscow)
location = Coordinate(14.66, 3.22)
print(moscow == location)

from collections import namedtuple
CoordinateNamedTuple = namedtuple("Coordinate", "lat lon")
print(issubclass(CoordinateNamedTuple, tuple))
kiev = CoordinateNamedTuple(24.02, 2.88)
print(kiev)
print(kiev == CoordinateNamedTuple(lat=24.02, lon=2.88))

import typing
#CoordinateTyping = typing.NamedTuple("Coordinate", [("lat", float), ("lon", float)])
#CoordinateTyping = typing.NamedTuple("Coordinate", lat=float, lon=float)
class CoordinateTyping(typing.NamedTuple):
    lat: float
    lon: float

    def __str__(self):
        ns = "N" if self.lat >= 0 else "S"
        we = "E" if self.lon >= 0 else "W"
        return f"{abs(self.lat):.1f}°{ns}, {abs(self.lon):.1f}°{we}"
print(issubclass(CoordinateTyping, tuple))
print(typing.get_type_hints(CoordinateTyping))

import dataclasses
from dataclasses import dataclass

@dataclass(frozen=True)
class CoordinateDataClass:
    lat: float
    lon: float

    def __str__(self):
        ns = "N" if self.lat >= 0 else "S"
        we = "E" if self.lon >= 0 else "W"
        return f"{abs(self.lat):.1f}°{ns}, {abs(self.lon):.1f}°{we}"

cdc = CoordinateDataClass(12.34, 45.78)
print(dataclasses.asdict(cdc))

# Классические именованные кортежи
City = namedtuple("City", "name country population coordinates")
tokyo = City(name="Tokyo",
             country="Japan",
             population=36.933,
             coordinates=(35.689722, 139.691667),
             )
print(tokyo.population)
print(tokyo[1])
print(City._fields)
Coordinate = namedtuple("Coordinate", "lat lon")
delhi_data = ("Delhi", "India", 21.935, Coordinate(28.613889, 77.208889))
delhi = City._make(delhi_data) #delhi = City(*delhi_data) - тоже самое
print(delhi._asdict())
import json
print(json.dumps(delhi._asdict()))

Coordinate = namedtuple("Coordinate", "lat lon reference", defaults=[15, "HH"]) #Значения по умолчанию для N самых правых полей класса
print(Coordinate(0))
print(Coordinate._field_defaults)

# Вставка метода в класс, созданный с помощью namedtuple (Хак, так лучше не делать, да и нахуй надо, собственно)
from deck import Deck
Card = namedtuple("Card", "rank suit")
Card.suit_values = dict(spades=3, hearts=2, diamonds=1, clubs=0)
def spades_high(card: Card):
    rank_value = Deck.ranks.index(card.rank)
    suit_value = card.suit_values[card.suit]
    return rank_value * len(card.suit_values) + suit_value
Card.overall_rank = spades_high
lower_card = Card("2", "clubs")
highest_card = Card("A", "spades")
print(lower_card.overall_rank())
print(highest_card.overall_rank())

# Типизированные именованные кортежи
