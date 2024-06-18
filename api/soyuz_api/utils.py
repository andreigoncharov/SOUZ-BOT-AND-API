import pyodbc


def get_error_message(exc):
    return f"Error Message: {exc}"


MSSQL_DB_NAME = 'Orders'
MSSQL_DB_HOST = '192.168.0.106'
MSSQL_DB_USER = 'SA'
MSSQL_DB_PASSWORD = 'Andrei12345'


class RemoteDbManager:
    mssqlserver_conn_str = 'DRIVER={ODBC Driver 17 for SQL Server};' \
                           + f'SERVER={MSSQL_DB_HOST};DATABASE={MSSQL_DB_NAME};UID={MSSQL_DB_USER};' \
                             f'PWD={MSSQL_DB_PASSWORD}'

    @staticmethod
    async def get_today_checkouts(expeditor_id, loop):
        conn = await loop.run_in_executor(None, lambda: pyodbc.connect(RemoteDbManager.mssqlserver_conn_str))
        cursor = conn.cursor()
        cursor.execute(f"""SELECT [CustomerId], [Status] FROM [Orders].[dbo].[ExpeditorCheckouts] 
        WHERE [ExpeditorId]='{expeditor_id}' AND CAST([TimeStamp] AS DATE) = cast(getDATE() as date)""")
        rows = cursor.fetchall()
        conn.close()
        return rows
