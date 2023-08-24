from collections import UserDict

class StrDictKey(UserDict):

    def __missing__(self, key):
        if isinstance(key, str):
            raise KeyError(key)
        return self.data[str(key)]

    def __setitem__(self, key, value):
        self.data[str(key)] = value

    def __contains__(self, key):
        return str(key) in self.data

sdk = StrDictKey()
sdk.update({1: "one", "2": "two"})
print(sdk.get(1))
print(sdk.get("1"))
print(sdk.get(3))
print(sdk)