import array
import random
import os
import bisect

# b - signet char, -128 - 127 (1 byte) - интерпретируется, как целое число

# floats = array.array("d", (random.random() for i in range(10**7)))
# print(floats[-1])
# file = open("floats.bin", "wb")
# floats.tofile(file)
# file.close()
#
# floats2 = array.array("d")
# file = open("floats.bin", "rb")
# floats2.fromfile(file, 10**7)
# file.close()
#
# print(floats2[-1])
#
# print(os.stat("floats.bin").st_size, "байт")

l = sorted([2, 3, 1])

bisect.insort(l, -1)
print(l)