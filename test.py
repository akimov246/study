from collections import Counter

c = Counter("aaabbc")
print(c)
c.update("cccbba")
print(*c.elements())