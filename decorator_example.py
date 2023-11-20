def benchmark(function):
    def wrapper():
        import time
        start = time.perf_counter()
        function()
        print(time.perf_counter() - start)
    return wrapper

@benchmark
def test():
    result = 2
    for i in range(1, 1000):
        result *= i
    return result

test()