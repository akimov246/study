from typing import NamedTuple

# User = NamedTuple('User', id = int, name = str)
#
# user = User(1, 'akimov246')
# print(user)

class User(NamedTuple):
    id: int
    name: str

user = User(2, 'akimoff246')
print(user)