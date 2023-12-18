# Класс в котором можно получать value  помошью ключа int или str
class StrKeyDict0(dict):
    # Метод __missing__ вызывается, когда с словаре нет нужного ключа
    def __missing__(self, key):
        if isinstance(key, str):
            raise KeyError(key)
        return self[str(key)]

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

    def __contains__(self, key):
        return key in self.keys() or str(key) in self.keys()

skd = StrKeyDict0()
skd.update({"1": "one", "2": "two", "3": "three"})
#print(skd[1])
#print(skd["1"])
#print(skd[2])
#print(skd["2"])
print(skd.get(3))