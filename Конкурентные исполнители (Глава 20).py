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