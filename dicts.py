import collections

dial_codes = [
    (880, "Bangladesh"),
    (55, "Brazil"),
    (86, "China"),
    (91, "India"),
    (62, "Indonesia"),
    (81, "Japan"),
    (234, "Nigeria"),
    (92, "Pakistan"),
    (7, "Russia"),
    (1, "United States"),
]

country_dial = {country: code for code, country in dial_codes}
print(country_dial)

country_dial = {code: country.upper()
                for country, code in sorted(country_dial.items())
                if code < 70}
print(country_dial)

def dump(**kwargs):
    return kwargs

print(dump(**{"x": 1}, y=2, **{"z": 3}))

d = {"a": 0, **{"x": 1}, "y": 2, **{"x":4, "z": 5}}
print(d)

d1 = {"a": 0, "b": 1}
d2 = {"a": 2, "b": 3, "c": 4}

print(d1 | d2)
d1 |= d2
print(d1)

def get_creators(record: dict) -> list:
    match record:
        case {"type": "book", "api": 2, "authors": [*names]}:
            return names
        case {"type": "book", "api": 1, "author": name}:
            return [name]
        case {"type": "book"}:
            raise ValueError(f"Invalid 'book' record: {record}")
        case {"type": "movie", "director": name}:
            return [name]
        case _:
            raise ValueError(f"Invalid record: {record}")

b1 = dict(api=1, author="Adolf Hitler",
          type="book", title="Mein Kampf")
print(get_creators(b1))

b2 = collections.OrderedDict(api=2, type="book",
                             title="Python in a Nutshell",
                             authors="Martelli Ravenscroft Holden".split())
print(get_creators(b2))
#print(get_creators({"type": "book", "page": 770}))

food = dict(category="ice cream", flavor="vanilla", cost=199)
match food:
    case {"category": "ice cream", **details}:
        print(f"Ice cream details: {details}")