import numpy
import random
from time import perf_counter

a = numpy.arange(12)
print(type(a))
print(a.shape)
a.shape = [3,4]
print(a)
print(a[:,1])
a = a.transpose()
print(a)

#file = open("floats-10M-lines.txt", "w")
#for i in range(10**7):
#    file.write(str(random.random()) + "\n")
#file.close()

floats = numpy.loadtxt("floats-10M-lines.txt")
print(floats[-3:])
floats *= 0.5
print(floats[-3:])
t0 = perf_counter()
floats /= 3
print(perf_counter() - t0)
numpy.save("floats-10M", floats)
floats2 = numpy.load("floats-10M.npy", "r+")
floats2 *= 6
print(floats2[-3:])


