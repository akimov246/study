import sqlite3

# Подключение/создание базы данных
con = sqlite3.connect("test.db")

# Как сопоставляются типы SQLite и Python:
"""SQLite | Python
   NULL   | None
   INTEGER| int
   REAL   | float
   TEXT   | str
   BLOB   | bytes
"""

# Для выполнения выражений SQL и получения данных из БД, необходимо создать курсор.
cursor = con.cursor()

# Для выполнения запросов и получения данных класс Cursor предоставляет ряд методов:
""" execute(sql, paramets=(), /) - Выполняет одну SQL-инструкцию.
    Через второй параметр в код SQL можно передать набор параметров в виде списка или словаря.
    
    executemany(sql, parametrs, /) - Выполняет параметризованную SQL-инструкцию.
    Через вторйо параметр принимает набор значений, которые передаются в выполняемый код SQL.
    
    executescript(sql_script, /) - Выполняет SQL-скрипт, который может включать множество SQL-инструкций.
    
    fetchone() - Возвращает одну строку в виде кортежа из полученного из БД набора строк.
    
    fetchmane(size=cursor.sizearray) - Возвращает набор строк в виде списка.
    Количетсво строк передается через параметр. Если строк в наборе нет, то возвращает пустой список.
    
    fetchall() - Возвращает все строки в виде списка."""

# Создание таблицы
cursor.execute("""CREATE TABLE people
                  (id INTEGER PRIMARY KEY AUTOINCREMENT,
                   name TEXT,
                   age INTEGER)""")