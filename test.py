import os
import sys

code = 9787
print(f"{code:x}")
print(hex(code))

dirs = os.listdir("./")
for dir in dirs:
    print(dir, os.path.getsize(dir), "байт")
