# Конкурентная загрузка из веба

# Скрипт последовательной загрузки

import time
from pathlib import Path
from typing import Callable

import httpx

POP20_CC = ('CN IN US ID BR PK NG BD RU JP MX PH VN ET EG DE IR TR CD FR').split()

BASE_URL = 'https://www.fluentpython.com/data/flags'
DEST_DIR = Path('downloaded')

def save_flag(img: bytes, filename: str) -> None:
    '''Скопировать img (последовательность байтов) в файл с именем filename в каталоге DEST_DIR'''
    (DEST_DIR / filename).write_bytes(img)

def get_flag(cc: str) -> bytes:
    '''Зная код страны, построить URL-адрес и загрузить изображение; вернуть двоичное содержимое ответа'''
    url = f'{BASE_URL}/{cc}/{cc}.gif'.lower()
    response = httpx.get(url,
                         timeout=6.1, # Тайм-аут, чтобы избежать ненужной блокировки на несколько минут
                         follow_redirects=True) # Разрешаем перенаправление (хотя тут оно не обязательно)
    response.raise_for_status() # В скрипте нет обработчика ошибок, но данный метод возбуждает исключение,
                                # если состояние HTTP не принадлежит диапазону 2XX (Успешно).
                                # Это рекомендуемая практика, позволяющая избежать "немых" отказов
    return response.content

def download_many(cc_list: list[str]) -> int:
    '''Основная функция, позволяющая провеси сравнение с конкурентными реализациями.
    Обойти список стран в алфавитном порядке, чтобы порядок отображения на выходе был такой же, как на входе;
    Вернуть количество загруженных изображений.'''
    for cc in sorted(cc_list):
        image = get_flag(cc)
        save_flag(image, f'{cc}.gif')
        print(cc, end=' ', flush=False) # flush=True необходим, потому что по умолчанию Python буферизует выходные строки, т.е.
                                       # напеатанные символы отображаются только после вывода символа перевода строки
    return len(cc_list)

def main(downloader: Callable[[list[str]], int]) -> None:
    '''При вызове main необходимо указывать функцию, которая производит загрузку;
    таким образом, main можно будет использовать, как библиотечную функцию, способную работать и с другими
    реализациями download_many в примерах threadpool и asyncio.'''
    DEST_DIR.mkdir(exist_ok=True) # Создать каталог DEST_DIR, если необходимо; не возбуждать исключение, если каталог уже существует
    t0 = time.perf_counter()
    count = downloader(POP20_CC)
    elapsed = time.perf_counter() - t0
    print(f'\n{count} downloads in {elapsed:.2f}s')

if __name__ == '__main__':
    main(download_many) # Вызвать main, передав ей фукнцию download_many

# Загрузка с применением библиотеки concurrent.futures

from concurrent import futures

def save_flag(img: bytes, filename: str) -> None:
    (DEST_DIR / filename).write_bytes(img)

def get_flag(cc: str) -> bytes:
    url = f'{BASE_URL}/{cc}/{cc}.gif'.lower()
    response = httpx.get(url, timeout=6.1, follow_redirects=True)
    response.raise_for_status()
    return response.content

def download_one(cc: str) -> str:
    '''Фунуция, загрудающая одно изображение; ее будет исполнять каждый поток'''
    image = get_flag(cc)
    save_flag(image, f'{cc}.gif')
    print(f'{cc}', end=' ')
    return cc

def download_many(cc_list: list[str]) -> int:
    '''Создать экземплятр ThreadPoolExecutor как контекстный менеджер;
    метод executor.__exit__ вызовет executor.shutdown(wait=True), который блокирует выполнение программы
    до завершения всех потоков'''
    with futures.ThreadPoolExecutor() as executor:
        res = executor.map(download_one, sorted(cc_list)) # Метод executor.map похож на встроенную функцию map с тем исключением,
                                                          # что функция download_one конкурентно вызывается из нескольких потоков;
                                                          # он возвращает генератор, который можно обойти для получения значений,
                                                          # возвращенных каждой функцией, - в данном случае каждое обращение к
                                                          # download_one возвращает код страны.

    return len(list(res)) # Вернуть количество полученных результатов. Если функция в каком-то потоке возбудит исключение,
                          # то оно возникнет в этом месте, когда неявный вызов next() из конструктора list попытается получить
                          # соотвествующее значение от итератора, возвращенного методом .map.

def main(downloader: Callable[[list[str]], int]) -> None:
    DEST_DIR.mkdir(exist_ok=True)
    t0 = time.perf_counter()
    count = downloader(POP20_CC)
    elapsed = time.perf_counter() - t0
    print(f'\n{count} downloads in {elapsed:.2f}s')

if __name__ == '__main__':
    main(download_many)

'''
Конструктор ThreadPoolExecutor принимет несколько аргументов, но первым и самым важным является max_workers, который
задает максимальное число исполняемых потоков. Если max_workers равно None (по умолчанию), то ThreadPoolExecutor вычисляет
значение по формуле max_workers = min(32, os.cpu_count() + 4).
Класс ThreadPoolExecutor повторно использует простаивающие рабочик потоки, прежде чем запускать max_workers исполнителей.
'''

# Где находятся будущие объекты?

# Замена executor.map на executor.submit и futures.as_completed (Пример использования будущих объектов)
def download_many(cc_list: list[str]) -> int:
    cc_list = cc_list[:5] # Для этой демонстрации мы ограничимсчя только пятью странами с самой большой численностью населения
    with futures.ThreadPoolExecutor(max_workers=3) as executor: # Установить значений max_workers равным 3, чтобы можно было следить
                                                                # за ожидающими будущими объеками в распечатке
        to_do: list[futures.Future] = []
        for cc in sorted(cc_list):
            future = executor.submit(download_one, cc) # Метод executor.submit планирует выполнение вызываемого объекта и
                                                       # возвращает объект future, представляющий ожидаемую операцию
            to_do.append(future) # Сохранить каждый будущий объект, чтобы впоследствии его можно было извлечь с помощью
                                 # функции as_completed
            print(f'Scheduled for {cc}: {future}')

        for count, future in enumerate(futures.as_completed(to_do), 1): # as_completed отдает будущие объекты по мере их завершения
            res: str = future.result() # получить результат этого объекта future
            print(f'{future} result: {res}')
    return count

if __name__ == '__main__':
    main(download_many)

# Запуск процессов с помощью concurrent.futures

import math

def is_prime(n: int) -> bool:
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    root = math.isqrt(n)
    for i in range(3, root + 1, 2):
        if n % i == 0:
            return False
    return True

NUMBERS = (2,
           142702110479723,
           299593572317531,
           3333333333333301,
           3333333333333333,
           3333335652092209,
           4444444444444423,
           4444444444444444,
           4444444488888889,
           5555553133149889,
           5555555555555503,
           5555555555555555,
           6666666666666666,
           6666666666666719,
           6666667141414921,
           7777777536340681,
           7777777777777753,
           7777777777777777,
           9999999999999917,
           9999999999999999)

import sys
from concurrent import futures
from time import perf_counter
from typing import NamedTuple

class PrimeResult(NamedTuple):
    n: int
    flag: bool
    elapsed: float

def check(n: int) -> PrimeResult:
    t0 = time.perf_counter()
    res = is_prime(n)
    return PrimeResult(n, res, time.perf_counter() - t0)

def main() -> None:
    if len(sys.argv) < 2:
        workers = None
    else:
        workers = int(sys.argv[1])

    executor = futures.ProcessPoolExecutor(workers)
    actual_workers = executor._max_workers # _max_workers - незадокументированный аттрибут экземпляра в классе ProcessPoolExecutor.
                                           # Показывает количество рабочих процессов

    print(f'Checking {len(NUMBERS)} numbers with {actual_workers} processes:')

    t0 = time.perf_counter()
    numbers = sorted(NUMBERS, reverse=True)
    with executor: # Используем executor как контекстный менеджер
        for n, prime, elapsed in executor.map(check, numbers):
            label = 'P' if prime else ' '
            print(f'{n:16} {label} {elapsed:9.6f}s')

        total_time = perf_counter() - t0
        print(f'Total time: {total_time:.2f}s')

if __name__ == '__main__':
    main()

# Почему кажется, что программа зависла, напечатав результат для 9999999999999999
'''
> Как уже отмечалось, executor.map(check, numbers) возвращает результаты в том же порядке, в каком заданы числа numbers.

> По умолчанию используется столько рабочих процессов, сколько имеется процессоров, - именно так ведет себя ProcessPoolExecutor,
когда max_workers равен None.

> Поскольку мы подаем numbers в порядке убывания, первое число равно 9999999999999999; у него есть делить 9, так что первая
проверка завершается быстро.

> Второе число равно 9999999999999917, это самое большое простое число в нашей выборке. На его проверку уходит больше времени, 
чем на проверку любого другого числа.

> Тем временем остальные процессы занимаются проверкой других чисел, которые являются либо простыми, либо составными с большими
множителями, либо составными с очень малыми множителями.

> Когда процесс, отвечающий за число 9999999999999917, наконец определит, что оно простое, все остальные процессы уже завершили 
работу, поэтому результаты появляются немедленно.
'''

# Эксперименты с executor.map

from time import sleep, strftime
from concurrent import futures

def display(*args):
    '''Эта фукнция печатает переданные ей аргументы, добавляя временную метку в формате [HH:MM:SS]'''
    print(strftime('[%H:%M:%S]'), end=' ')
    print(*args)

def loiter(n):
    '''Эта функция печатает время начала работы, затем спит n секунд и печатает время окончания;
    знаки табуляции формируют отступ сообщения в соответствии с величиной n'''
    msg = '{}loiter({}): doing nothing for {}s...'
    display(msg.format('\t'*n, n, n))
    sleep(n)
    msg = '{}loiter({}): done.'
    display(msg.format('\t'*n, n))
    return n * 10

def main():
    display('Script starting')
    executor = futures.ThreadPoolExecutor(max_workers=3) # Создать объект ThreadPoolExecutor с тремя потоками
    results = executor.map(loiter, range(5)) # Передать исполнителю executor пять задач (поскольку есть только три потока,
                                             # сразу начнут выполнение лишь три из них); это неблокирующий вызов.
    display('results: ', results) # Немедленно распечатать объект results, полученный от executor.map: это генератор.
    display('Waiting for individual results:')
    for i, result in enumerate(results):
        '''Обращение к enumerate в цикле for неявно вызывает функцию next(results), которая, в свою очередь, вызывает 
        метод _f.result() (внутреннего) будущего объекта _f, представляющего первый вызов, loiter(0).
        Метод result блокирует программу до завершения будущего объекта, поэтому каждая итерация цикла будет ждать готовности
        следующего результата'''
        display(f'result {i}: {result}')

if __name__ == '__main__':
    main()

'''
Функцией executor.map пользоваться легко, но зачастую желательно получать результаты по мере готовности вне зависимости от 
порядка подачи исходных данных. Для этого нужна комбинация метода executor.submit и функции futures.as_completed.

Комбинация executor.sumbit и futures.as_completed обладает большей гибкостью, чем executor.map, потому что ей можно подавать
различные вызываемые объекты и аргументы, тогда как executor.map предназначен для выполнения одного  и того же вызываемого 
объекта с разными агументами. Кроме того, множество будущих объектов, передаваемых futures.as_completed, может поступать от
нескольких - одни из них могли быть созданы экземпляром ThreadPoolExecutor, другие - экземпляром ProcessPoolExecutor.
'''

# Загрузка с индикацией хода выполнения и обработкой ошибок
# Настройка тестовых серверов
'''
1. git clone https://github.com/fluentpython/example-code-2e.git
2. Перейти в exaple-code-2e/20-executors/getflags
3. Разархировать flags.zip в exaple-code-2e/20-executors/getflags/flags
4. Открыть консоль, перейти в папку exaple-code-2e/20-executors/getflags и запустить python.exe -m http.server.
Это запустит ThreadingHTTPServer на 8000 порту, обслуживающий локальные файлы.
Если открыть http://localhost:8000/flags/ в своем браузере, можно увидеть длинный список каталогов, названных двухбуквенными
кодами стран от ad/ до zw/.
'''

'''
Очень полезно при работе с функцией futures.as_completed построить словарь, ставящий в соответствие каждому будущему объекту
данные, которые можно будет использовать по завершении этого объекта.
'''