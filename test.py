import asyncio
import pyodbc

async def execute_query():
    loop = asyncio.get_running_loop()

    # Создаем подключение к базе данных
    conn = await loop.run_in_executor(None, lambda: pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=Expeditors;UID=SA;PWD=Andrei12345'))

    # Создаем курсор для выполнения запросов
    cursor = conn.cursor()

    # Выполняем SQL-запрос
    cursor.execute("SELECT * FROM Expeditors")

    # Получаем результаты запроса
    rows = cursor.fetchall()

    # Выводим результаты на экран
    for row in rows:
        print(row)

    # Закрываем соединение
    conn.close()

# Запускаем асинхронную функцию execute_query()
asyncio.run(execute_query())
