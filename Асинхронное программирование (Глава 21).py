'''
> Платформенная сопрограмма - функция, определенная с помощью конструкции async def. Мы можем делегировать работу от одной
платформенной сопрограммы другой, воспользовавшись клюевым словом await, по аналогии с тем, как классические сопрограммы уступают
управление с помощью предложения yield from. Предложение async def всегда определяет платформенную спорограмму, даже
если в ее теле не встречается ключевое слово await. Слово await нельзя использовать вне платформенной сопрограммы.

> Классическая сопрограмма - генераторная функция, которая потребляет данные, отправленные ей с помозью вызовов my_coro.send(data),
и читает эти данные, используя yield в выражении. Классическая сопрограмма может делигировать работу другой классической сопрограмме
с помощью предложения yield from. Классические сопрограммы не приводятся в действие словом await и более не поддерживаются
библиотекой asyncio.

> Генераторные сопрограммы - генераторная фукнция, снабженная декоратором @types.coroutine. Этот декоратор делает генератор
совместимым с новым ключевым словом await.

> Асинхронный генератор - генераторная функция, определенная с помощью конструкции async def и содержащая в теле yield.
Она возвращает асинхронный объект-генератор, предоставляющий метод __anext__ для асинхронного получения следующего значения.
'''

# Пример использования asyncio: проверка доменных имен
'''
Допустим, вы собираетесь начать новый блог, посвященный Python, и планируете зарегистрировать домен, содержащий какое-нибудь 
клюевое слово Python и имеющий суффикс .DEV, например AWAIT.DEV.
'''

import asyncio
import socket
from keyword import kwlist

MAX_KEYWORD_LEN = 4 # Задать максимальную длину ключевого слова в доменном имени, поскольку чем оно короче, тем лучше.

async def probe(domain: str) -> tuple[str, bool]:
    '''Функция probe возвращает кортеж, содержащий доменное имя и булево знаение; True означает, что имя успешно разрешено.
    Возврат доменного имени упрощает отображение результатов.'''
    loop = asyncio.get_running_loop() # Получить ссылку на цикл событий asyncio для будущего использования.
    try:
        await loop.getaddrinfo(domain, None) # Метод-сопрограмма loop.getaddrinfo(...) возвращает 5-кортеж параметров для
                                             # подключения к указанному адресу через сокет. В этом примере нам результат не нужен.
                                             # Если мы получили кортеж, значит, имя разрешено, в противном случае - нет.
    except socket.gaierror:
        return (domain, False)
    return (domain, True)

async def main() -> None: # Должна быть сопрограммой, чтобы в ней можно было использовать await
    names = (kw for kw in kwlist if len(kw) <= MAX_KEYWORD_LEN) # Генератор, отдающий ключевые слова Python длиной не более MAX_KEYWORD_LEN.
    domains = (f'{name}.dev'.lower() for name in names) # Генератор, отдающий доменные имена с суффиксом .dev.
    coros = [probe(domain) for domain in domains] # Построим список объектов сопрограмм, вызывая сопрограмму probe с каждым аргументом domain.
    for coro in asyncio.as_completed(coros): # asyncio.as_completed - генератор, отдающий переданные ему сопрограммы в порядке
                                             # их завершения, а не в порядке подачи. Он похож на функцию futures.as_completed.
        domain, found = await coro # В этот момент вы знаем, что сопрограмма завершилась, потому то так работает as_completed.
                                   # Поэтому выражение await не заблокирует выполнение, но оно все равно необходимо, чтобы получить
                                   # результат от coro. Если coro возбуждала необработанное исключение, то оно будет заново
                                   # возбуждено в этой точке.
        mark = '+' if found else ' '
        print(f'{mark} {domain}')

if __name__ == '__main__':
    asyncio.run(main()) # asyncio.run запускает цикл событий и возвращает управление только после выхода из него.
                        # Это типичный паттерн для скриптов, в которых используется asyncio: реализовать main как сопрограмму и
                        # выполнить ее внутри блока if __name__ == '__main__':.

'''
Функция asyncio.get_running_loop была добавлена для использования внутри сопрограмм, как показано в probe. Если работающего 
цикла нет, то она возбуждает исключение RuntimeError. Ее реализация проще и быстрее, чем реализация функции asyncio.get_event_loop, 
которая может при необходимости запустить цикл событий. asyncio.get_event_loop объявлена нерекомендуемой и в конечном итоге станет
псевдонимом asyncio.get_running_loop.
'''

# Предложенный Гвидо способ чтения асинхронного кода
'''
Общий прием - прищуриться и сделать вид, что ключевых слов async и await нет. Тогда вы моймете, что сопрограммы читаются, как
старые добрые последовательные фукнции, с тем отличием, что волшебным образом никогда не блокируется выполнение сопрограммы.

Конструкция await loop.getaddrinfo(...) позволяет избежать блокирования, потому что await приостанавливает текущий объект сопрограммы.
Например, во время выполнения сопрограммы probe('if.dev') создается новый объект сопрограммы с помощью вызова 
getaddrinfo('if.dev', None). Его ожидание запускает низкоуровневый запрос addrinfo и уступает управление циклу событий, а не 
приостановленной сопрограмме probe('if.dev'). Затем цикл событий может передать управление другим ожидающим объектам сопрограмм,
например probe('or.dev').
Когда цикл событий получитответ от запроса getaddrinfo('if.dev', None), этот объект сопрограммы возобновляется и возвращает 
управление probe('if.dev'), которая была приостановлена в await, а затем может обработать возможное исключение и вернуть кортеж
с результатами.
'''

# Загрузка файлов с помощью asyncio и httpx

import asyncio
import time

from pathlib import Path
from httpx import AsyncClient
from typing import Callable

POP20_CC = ('CN IN US ID BR PK NG BD RU JP MX PH VN ET EG DE IR TR CD FR').split()

BASE_URL = 'https://www.fluentpython.com/data/flags'
DEST_DIR = Path('downloaded')

def save_flag(img: bytes, filename: str) -> None:
    '''Скопировать img (последовательность байтов) в файл с именем filename в каталоге DEST_DIR'''
    (DEST_DIR / filename).write_bytes(img)

def download_many(cc_list: list[str]) -> int:
    '''Это должна быть обычная функция, а не сопрограмма, чтобы ее можно было передать и вызвать из функции main.
    Выполнять цикл событий, приводящий в действие объект сопрограммы supervisor(cc_list), пока тот не вернет управление.
    Эта строка блокирует выполнение на все время работы цикла событий. Ее результатом является значение, возвращенное supervisor.'''
    return asyncio.run(supervisor(cc_list))

async def download_one(client: AsyncClient, cc: str) -> str:
    '''Должна быть платформенной сопрограммой, чтобы она могла вызвать await для сопрограммы get_flag, которая выполняет
    http-запрос. Затем она отображает загруженный флаг и сохраняет изображение.'''
    image = await get_flag(client, cc)
    save_flag(image, f'{cc}.gif')
    print(cc, end=' ', flush=True)
    return cc

async def get_flag(client: AsyncClient, cc: str) -> bytes: # Должна получить AsyncClient, чтобы сделать запрос.
    url = f'{BASE_URL}/{cc}/{cc}.gif'.lower()
    resp = await client.get(url, timeout=6.1, follow_redirects=True) # Метод get экземпляра httpx.AsyncClient возвращает объект
                                                                     # ClientResponse, который заодно является асинхронным
                                                                     # контекстным менеджером.

    return resp.read() # Операции сетевого ввода-вывода реализованы в виде методов-сопрограмм, чтобы их можно было асинхронно
                       # вызвать из цикла событий asyncio.

async def supervisor(cc_list: list[str]) -> int:
    async with AsyncClient() as client: # Асинхронные операции HTTPX-клиета в httpx - это методы класса AsyncClient, который также
                                        # является асинхронным контекстным менеджером, т.е. контекстным менеджером с асинхронными
                                        # методами инициализации и очистки.
        to_do = [download_one(client, cc) for cc in sorted(cc_list)] # Построить список объектов сопрограм, вызвав сопрограмму
                                                                     # download_one по разу для каждого флага.
        res = await asyncio.gather(*to_do) # Ждать завершения сопрограммы asyncio.gather, которая принимает один или несколько
                                          # допускающих ожидание аргументов, ждет их завершения, а затем возвращает список
                                          # результатов заданных объектов в том порядке, в каком они подавались на вход.

    return len(res) # Возвращает длину списка, возвращенного функцией asyncio.gather.

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
    main(download_many)

# Асинхронные контекстные менеджеры
'''
Реализация классического предложения with не поддерживает выполнение методов __enter__ и __exit__ сопрограммами. Поэтому было
введено предложение async with, работающее с асинхронными контекстными менеджерами: объектами, реализующими методы
__aenter__ и __aexit__ как сопрограммы.
'''

# Улучшение асинхронного загрузчика
# Использование asyncio.as_completed и потока

import asyncio
from enum import Enum
from collections import Counter
from http import HTTPStatus
from pathlib import Path

import httpx
import tqdm

# По умолчанию задана низкая степень конкурентности, чтобы избежать ошибок удаленного сайта,
# например 503 - Service Temporarily Unavalible

DEFAULT_CONCUR_REQ = 5
MAX_CONCUR_REQ = 1000

DEST_DIR = Path('downloaded')

POP20_CC = ('CN IN US ID BR PK NG BD RU JP MX PH VN ET EG DE IR TR CD FR').split()
BASE_URL = 'https://www.fluentpython.com/data/flags'

DownloadStatus = Enum('DownloadStatus', 'OK NOT_FOUND ERROR')

def save_flag(img: bytes, filename: str) -> None:
    (DEST_DIR / filename).write_bytes(img)

async def get_flag(client: httpx.AsyncClient, base_url: str, cc: str) -> bytes:
    url = f'{base_url}/{cc}/{cc}.gif'.lower()
    response = await client.get(url, timeout=6.1, follow_redirects=True)
    response.raise_for_status()
    return response.content

async def download_one(client: httpx.AsyncClient,
                       cc: str,
                       base_url: str,
                       semaphore: asyncio.Semaphore,
                       vervose: bool) -> DownloadStatus:
    try:
        async with semaphore: # Использовать semaphore как асинхронный контекстный менеджер, чтобы не блокировать программу
                              # целиком; только эта сопрограмма приостанавливается, когда счетчик семафора обращается в нуль.
            image = await get_flag(client, base_url, cc)
    except httpx.HTTPStatusError as exc:
        res = exc.response
        if res.status_code == HTTPStatus.NOT_FOUND:
            status = DownloadStatus.NOT_FOUND
            msg = f'not found: {res.url}'
        else:
            raise
    else:
        await asyncio.to_thread(save_flag, image, f'{cc}.gif') # Сохранение изображения - операция ввода-вывода. Чтобы избежать
                                                               # блокирования цикла событий, функция save_flag выполняется в
                                                               # отдельном потоке.
        status = DownloadStatus.OK
        msg = 'OK'
    if vervose and msg:
        print(cc, msg)
    return status

async def supervisor(cc_list: list[str], base_url: str, verbose: bool, concur_req: int) -> Counter[DownloadStatus]:
    '''supervisor принимает те же аргументы что фугкция download_many, но ее нельзя вызывать из main напрямую, потому
    что это сопрограмма, а не обычная функция'''
    counter: Counter[DownloadStatus] = Counter()
    semaphore = asyncio.Semaphore(concur_req) # Создать семафор asyncio.Semaphore, которым смогут одновременно пользоваться
                                              # не более concur_req сопрограмм.
    async with httpx.AsyncClient() as client:
        # Создать список объектов сопрограмм, по одному на каждый вызов сопрограммы download_one
        to_do = [download_one(client, cc, base_url, semaphore, verbose) for cc in sorted(cc_list)]
        to_do_iter = asyncio.as_completed(to_do) # Получить итератор, который будет возвращать объекты сопрограмм по мере их
                                                 # завершения.
        if not verbose:
            to_do_iter = tqdm.tqdm(to_do_iter, total=len(cc_list)) # Обернуть итератор as_completed генераторной функцией tqdm,
                                                                   # чтобы показать индикатор хода выполнения
        error: httpx.HTTPError | None = None # Объявить переменную error и инициализировать ее значением None; в этой переменной
                                             # мы будем хранить исключение за пределами предложения try/except, если такое возникнет.
        for coro in to_do_iter: # Обойти завершившиеся объекты сопрограмм.
            try:
                status = await coro # Ждать завершения сопрограммы для получения результата. Это предложение не приводит к
                                    # блокированию, потому что as_completed порождает только уже завершившиеся сопрограммы.
            except httpx.HTTPStatusError as exc:
                resp = exc.response
                error_msg = f'HTTP error {resp.status_code} - {resp.reason_phrase}'
                error = exc # Это присваивание необходимо, поскольку область видимости переменной exc ограничена этой
                            # ветвью except.
            except httpx.RequestError as exc:
                error_msg = f'{exc} {type(exc)}'.strip()
                error = exc
            except KeyboardInterrupt:
                break

            if error:
                status = DownloadStatus.ERROR # Если была ошибка, установить переменную status.
                if verbose:
                    url = str(error.request.url) # В режиме подробной диагностики извлечь url-адрес из возникшего исключения.
                    cc = Path(url).stem.upper() # и имя файла, чтобы показать код страны.
                    print(f'{cc} error: {error_msg}')
            counter[status] += 1
    return counter

def download_many(cc_list: list[str], base_url: str, verbose: bool, concur_req: int) -> Counter[DownloadStatus]:
    coro = supervisor(cc_list, base_url, verbose, concur_req)
    counts = asyncio.run(coro) # download_many создает объект сопрограммы supervisor и передает его циклу событий,
                               # вызвав asyncio.run, а затем получаем счетчик, который supervisor возвращает по завершении цикла событий.

    return counts

def main(download_many, default_concur_req, max_concur_req):
    cc_list = sorted(POP20_CC)
    actual_req = min(max_concur_req, len(cc_list))
    base_url = BASE_URL
    DEST_DIR.mkdir(exist_ok=True)
    t0 = time.perf_counter()
    counter = download_many(cc_list, base_url, False, actual_req)
    print(counter)
    print(time.perf_counter() - t0)

if __name__ == '__main__':
    main(download_many, DEFAULT_CONCUR_REQ, MAX_CONCUR_REQ)

# Регулирование темпа запросов с помощью семафоров
'''
Сетевые клиенты типа рассматриваемого здесь следует дросселировать (т.е. ограничивать), чтобы избежать затопления сервера
слишком большим количеством конкурентных запросов.
Семафор - это примитив синхронизации, более гибкий, чем блокировка. Симафор могут удерживать несколько сопрограмм, причем
максимальное их число настраивается. Поэтому это идеальный механизм для ограничения количества активных конкуретных сопрограмм.

В классе asyncio.Semaphore имеется внутренний счетчик, который уменьшается на 1 всякий раз, как выполняется await для
метода-сопрограммы .acquire(), и увеличивается на 1 при вызове метода .release(), который не является сопрограммой, потому что
никогда не блокирует выполнение. Начальное значение счетчика задается при создании объекта Semaphore:
    semaphore = asyncio.Semaphore(concur_req)
Ожидание .acquire() не приводит к задержке, когда счетчик больше 0, но если счетчик равен 0, то .acquire() приостанавливает
ожидающую сопрограмму до тех пор, пока какая-нибудь другая сопрограмма не вызовет .release() для того же семафора, увеличив
тем самым счетчик. Вместо того чтобы обращаться к этим методам напрямую, безопаснее использовать semaphore как асинхронный
контекстный менеджер.
    await with semaphore:
        image = await get_flag(client, base_url, cc)
Метод-сопрограмма Semaphore.__aenter__ ждет завершения .acquire(), а метод завершения __aexit__ вызывает .release().
Этот код гарантирует, что в любой момент времени будет активно не более concur_req экземпляров сопрограммы get_flag.
У каждого из классов Semaphore в стандартной библиотеке имеется подкласс BoundedSemaphore, налагающий дополнительное
ограничение: внутренний счетчик не может стать больше начального значения, если операций .release() окажется больше, 
чем .acquire().
'''

# Отправка нескольких запросов при каждой загрузке
'''
Предположим, что мы хотим сохранить вместе с флагом каждой страны ее название и код, а не только код. Тогда нужно отправить
два HTTP-запроса на каждый флаг: один для получения самого изображения флага, а другой для получения файла metadata.json, 
находящегося в том же каталоге, что изображение, - именно там хранится название страны.
'''

async def get_country(client: httpx.AsyncClient, base_url: str, cc: str) -> str: # Возвращает название страны, если всё пройдет хорошо.
    url = f'{base_url}/{cc}/metadata.json'.lower()
    response = await client.get(url, timeout=6.1, follow_redirects=True)
    response.raise_for_status()
    metadata = response.json() # В metadata будет находиться словарь Python, построенный по содержимому ответа в формате JSON.
    return metadata['country'] # Вернуть название страны

async def download_one(client: httpx.AsyncClient,
                       cc: str,
                       base_url: str,
                       semaphore: asyncio.Semaphore,
                       verbose: bool) -> DownloadStatus:
    try:
        async with semaphore: # Удерживать семафор, чтобы дождаться результата get_flag
            image = await get_flag(client, cc)
        async with semaphore: # и еще раз для ожидания get_country
            country = await get_country(client, base_url, cc)
    except httpx.HTTPStatusError as exc:
        res = exc.response
        if res.status_code == HTTPStatus.NOT_FOUND:
            status = DownloadStatus.NOT_FOUND
            msg = f'not found: {res.url}'
        else:
            raise
    else:
        filename = country.replace(' ', '_') # Использовать название страны для создания нового файла
        await asyncio.to_thread(save_flag, image, f'{filename}.gif')
        status = DownloadStatus.OK
        msg = 'OK'
    if verbose and msg:
        print(cc, msg)
    return status

# Написание асинхронных серверов

import sys
import unicodedata
from collections import defaultdict
from collections.abc import Iterator

STOP_CODE: int = sys.maxunicode + 1
Char = str
Index = defaultdict[str, set[Char]]

def tokenize(text: str) -> Iterator[str]:
    '''Возвращает итератор слов в высоком регистре'''
    for word in text.upper().replace('-', ' ').split():
        yield word

class InvertedIndex:
    entries: Index

    def __init__(self, start: int = 32, stop: int = STOP_CODE):
        entries: Index = defaultdict(set)
        for char in (chr(i) for i in range(start, stop)):
            name = unicodedata.name(char, '')
            if name:
                for word in tokenize(name):
                    entries[word].add(char)
        self.entries = entries

    def search(self, query: str) -> set[Char]:
        if words := list(tokenize(query)):
            found = self.entries[words[0]]
            return found.intersection(*(self.entries[w] for w in words[1:]))
        else:
            return set()

def format_results(chars: set[Char]) -> Iterator[str]:
    for char in sorted(chars):
        name = unicodedata.name(char)
        code = ord(char)
        yield f'U+{code:04X}\t{char}\t{name}'

def main(words: list[str]) -> None:
    if not words:
        print('Please give one or more words to search.')
        sys.exit(2)
    index = InvertedIndex()
    chars = index.search(' '.join(words))
    for line in format_results(chars):
        print(line)
    print('-' * 66, f'{len(chars)} found')

if __name__ == '__main__':
    main('cat face'.split())

# Веб-служба FastAPI

# Следующая команда запускает код с uvicorn в режиме разработки:
# uvicorn web_mojifinder:app --reload
# Параметры:
# web_mojifinder:app - имя пакета, двоеточие и имя определенного в нем ASGI-приложения; по соглашению, приложения часто называют app
# --reload - поручить uvicorn отслеживать изменения в исходных файлах приложения и автоматически перегружать их. Полезно только на этапе разработки.

# web_mojifinder.py
from pathlib import Path
from unicodedata import name

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

STATIC_PATH = Path(__file__).parent.absolute() / 'static'

# В этой строке определяется ASGI-приложение. Достаточно было написать app = FastAPI(). Показанные параметры - это метаданные
# для автоматического генерирования документации.
app = FastAPI(title='Mojifinder Web',
              description='Search for Unicode characters by name.')

class CharName(BaseModel): # Пидантическая форма JSON-ответа с полями char и name.
    char: str
    name: str

def init(app): # Построить индекс и загрузить статическую HTML-форму, присоединив то и другое к app.state для последующего использования
    app.state.index = InvertedIndex()
    app.state.form = (STATIC_PATH / 'form.html').read_text()

init(app) # Выполнить init в момент загрузки этого модуля ASGI-сервером.

# Маршрут к оконечной точке /search; response_model использует пидантическую модель CharName для описания формата ответа
@app.get('/search', response_model=list[CharName])
async def search(q: str):
    '''FastAPI предполагает, что параметры, встречающиеся в сигнатуре функции или сопрограммы, но не присутствующие
    в пути маршрута, передаются в строке HTTP-запроса, например /search?q=cat.
    Поскольку для q не задано значение по умоланию, FastAPI вернет код состояния 422 (Unprocessable Entity),
    если q отсуствует в строке запроса.'''
    chars = sorted(app.state.index.search(q))
    return ({'char': c, 'name': name(c)} for c in chars) # Возврат итерируемого объекта, состоящего из словарей и совместимого
                                                         # со схемой response_model, позволяет FastAPI построить JSON-ответ
                                                         # в соответствии со схемой response_model, заданной в декораторе @app.get.

@app.get('/', response_class=HTMLResponse, include_in_schema=False)
def form(): # Обычные (не асинхронные) функции тоже можно использовать для генерирования ответов.
    return app.state.form # В этом модуле нет функции main. Он загружается и выполняется ASGI-сервером - в данном случае uvicorn.