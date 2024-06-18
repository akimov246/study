import asyncio
import time

from string import ascii_uppercase

async def coro1():
    for i in range(10):
        print(i)
        await asyncio.sleep(1)
    return 'Return от coro1'

async def coro2():
    for char in ascii_uppercase:
        print(char)
        await asyncio.sleep(0.5)
    return 'Return от coro2'

async def main():
    to_do = [coro1(), coro2()]
    for coro in asyncio.as_completed(to_do):
        res = await coro
        print(res)


asyncio.run(main())