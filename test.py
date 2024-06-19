import asyncio

# Exercise 1
async def exercise1(msg: str) -> None:
    await asyncio.sleep(2)
    print(msg)

if __name__ == '__main__':
    asyncio.run(exercise1('Python Exercises!'))

# Exercise 2
async def coro1():
    await asyncio.sleep(1)
    print('coro1')

async def coro2():
    await asyncio.sleep(2)
    print('coro2')

async def coro3():
    await asyncio.sleep(3)
    print('coro3')

async def main():
    await asyncio.gather(coro1(), coro2(), coro3())

if __name__ == '__main__':
    asyncio.run(main())

# Exerciese 3

async def coro():
    for i in range(1, 8):
        print(i)
        await asyncio.sleep(0.5)

asyncio.run(coro())

# Exercise 4, 5

from httpx import AsyncClient
from typing import NamedTuple
import time
import random

urls = 'https://peopleandblogs.com/ https://www.siteinspire.com/'.split()

class DownloadResult(NamedTuple):
    url: str
    content: bytes
    elapsed: float

async def download_one(client: AsyncClient, url: str) -> DownloadResult:
    t0 = time.perf_counter()
    response = await client.get(url, timeout=6.1)
    #response.raise_for_status()
    return DownloadResult(url, response.content, time.perf_counter() - t0)

async def download_many():
    async with AsyncClient() as client:
        t0 = time.perf_counter()
        to_do = [download_one(client, url) for url in urls]

        for coro in asyncio.as_completed(to_do):
            url, content, elapse = await coro
            print(url, content[:100])
            print(elapse)

        print(time.perf_counter() - t0)

if __name__ == '__main__':
    asyncio.run(download_many())

# Exercise 6

async def hard_work_imit():
    await asyncio.sleep(3)
    if random.randint(1, 2) % 2:
        raise asyncio.CancelledError
    else:
        return 'OK'

async def main():
    try:
        res = await hard_work_imit()
    except asyncio.CancelledError:
        print('Ошибочка вылезла')
    else:
        print(res)

if __name__ == '__main__':
    asyncio.run(main())

# Exercise 7

async def to_be_or_not_to_be():
    await asyncio.sleep(random.randint(1, 5))
    return 'OK'

async def main():
    try:
        res = await asyncio.wait_for(to_be_or_not_to_be(), timeout=3.1)
    except asyncio.TimeoutError:
        print('Timeout!')
    else:
        print(res)

if __name__ == '__main__':
    asyncio.run(main())