import asyncio
import time

from pymysql import connect
import aiomysql
from .config import *
from .models import *
import pyodbc


async def create_con(loop):
    con = await aiomysql.connect(host=MYSQL_DB_HOST, user=MYSQL_DB_USER, db=MYSQL_DB_NAME, password=MYSQL_DB_PASSWORD, loop=loop)
    cur = await con.cursor()
    return con, cur


def create_sync_con():
    con = connect(host=MYSQL_DB_HOST, user=MYSQL_DB_USER, db=MYSQL_DB_NAME, password=MYSQL_DB_PASSWORD)
    cur = con.cursor()
    return con, cur


class RemoteDbManager:

    def __init__(self):
        self.mssqlserver_conn_str = 'DRIVER={ODBC Driver 17 for SQL Server};' \
                           + f'SERVER={MSSQL_DB_HOST};DATABASE={MSSQL_DB_NAME};UID={MSSQL_DB_USER};' \
                             f'PWD={MSSQL_DB_PASSWORD}'
        self.conn = None
        self.conn = self.get_conn()

    def get_conn(self, loop=None):
        if self.conn:
            try:
                cursor = self.conn.cursor()
                cursor.execute("""SELECT TOP(1) [DateTime]
,[ExpeditorId]
,[Expeditor]
,[CustomerId]
,[Customer]
,[Comment]
,[Order]
,[Route]
,[DriverID]
,[Driver]
,[AgentID]
,[DESCR]
,[TimeStamp]
,[CheckStatus] from [Orders].[dbo].[{VIEW_NAME}];""")
                cursor.fetchall()
                return self.conn
            except pyodbc.Error as e:
                conn = pyodbc.connect(self.mssqlserver_conn_str)
                return conn
        else:
            conn = pyodbc.connect(self.mssqlserver_conn_str)
            return conn

    async def get_expeditors(self, loop):
        print("get_conn")
        t1 = time.time()
        conn = self.get_conn(loop)
        print("get_conn time: ", time.time() - t1)
        print("continue")
        t1 = time.time()
        cursor = conn.cursor()
        cursor.execute(
            f"""SELECT DISTINCT [ExpeditorId], [Expeditor] FROM [Orders].[dbo].[{VIEW_NAME}];""")
        rows = cursor.fetchall()
        conn.close()
        print("finish time: ", time.time() - t1)
        return rows

    async def get_all_expeditors(self, agent_id, loop):
        conn = self.get_conn(loop)
        cursor = conn.cursor()
        cursor.execute(f"""SELECT DISTINCT [ExpeditorId], [Expeditor] FROM [Orders].[dbo].[{VIEW_NAME}] where LTRIM(RTRIM([AgentID])) = '{agent_id}';""")
        rows = cursor.fetchall()
        conn.close()
        return rows

    async def get_clients(self, agent_id, loop):
        conn = self.get_conn(loop)
        cursor = conn.cursor()
        cursor.execute(f"""SELECT [CustomerID], [Customer], [ExpeditorId], [Expeditor], 
        [DriverID], [Driver], [Route], [TimeStamp], [CheckStatus], [Order]
        FROM [Orders].[dbo].[{VIEW_NAME}] where LTRIM(RTRIM([AgentID])) = '{agent_id}';""")
        rows = cursor.fetchall()
        conn.close()
        return rows

    async def get_client_names(self, agent_id, loop):
        conn = self.get_conn(loop)
        cursor = conn.cursor()
        cursor.execute(f"""SELECT [CustomerID], [Customer]
            FROM [Orders].[dbo].[{VIEW_NAME}] where LTRIM(RTRIM([AgentID])) = '{agent_id}';""")
        rows = cursor.fetchall()
        conn.close()
        return rows

    async def get_client_info(self, customer_id, loop):
        conn = self.get_conn(loop)
        cursor = conn.cursor()
        cursor.execute(f"""SELECT [CustomerID], [Customer], [ExpeditorId], [Expeditor], 
            [DriverID], [Driver], [Route], [TimeStamp], [CheckStatus], [Order]
            FROM [Orders].[dbo].[{VIEW_NAME}] where [CustomerId] = '{customer_id}';""")
        rows = cursor.fetchall()
        conn.close()
        return rows

    async def get_unique_expeditor_routes_by_agent(self, agent_id,  loop):
        conn = self.get_conn(loop)
        cursor = conn.cursor()
        cursor.execute(f"""SELECT DISTINCT [ExpeditorId], [Route]
                              FROM [Orders].[dbo].[{VIEW_NAME}] where LTRIM(RTRIM([AgentID])) = '{agent_id}';""")
        rows = cursor.fetchall()
        conn.close()
        return rows

    async def get_expeditor_last_checkin(self, expeditor_id, route, loop):
        conn = self.get_conn(loop)
        cursor = conn.cursor()
        cursor.execute(f"""SELECT 
    [ExpeditorId],
    [Route],
    MAX([Order]) AS MaxOrder
FROM [Orders].[dbo].[{VIEW_NAME}]
WHERE LTRIM(RTRIM([ExpeditorId])) = '{expeditor_id}' 
  AND [TimeStamp] IS NOT NULL AND ROUTE={route}
GROUP BY [ExpeditorId], [Route];
""")
        rows = cursor.fetchall()
        conn.close()
        return rows

    async def get_expeditor_clients_by_agent(self, agent_id, expeditor_id, loop):
        conn = self.get_conn(loop)
        cursor = conn.cursor()
        cursor.execute(f"""SELECT [Expeditor], [CustomerId], [Customer], [Route], [Order], [TimeStamp], [CheckStatus]
FROM [Orders].[dbo].[{VIEW_NAME}]
WHERE LTRIM(RTRIM([AgentID])) = '{agent_id}' AND LTRIM(RTRIM([ExpeditorId]))='{expeditor_id}'
ORDER BY [Route], [Order];""")
        rows = cursor.fetchall()
        conn.close()
        return rows

    async def get_expeditor_clients(self, expeditor_id, loop):
        conn = self.get_conn(loop)
        cursor = conn.cursor()
        cursor.execute(f"""SELECT [Expeditor], [CustomerId], [Customer], [Route], [Order], [TimeStamp], [CheckStatus]
FROM [Orders].[dbo].[{VIEW_NAME}]
WHERE LTRIM(RTRIM([ExpeditorId]))='{expeditor_id}'
ORDER BY [Route], [Order];""")
        rows = cursor.fetchall()
        conn.close()
        return rows

    async def get_agent_description(self, agent_id, loop):
        conn = self.get_conn(loop)
        cursor = conn.cursor()
        cursor.execute(f"""SELECT [ID], [DESCR] FROM [Orders].[dbo].[agent_info]
WHERE LTRIM(RTRIM([ID])) = '{agent_id}';""")
        rows = cursor.fetchall()
        conn.close()
        return rows


class UsersDbManager:
    @staticmethod
    def clear():
        con, cur = create_sync_con()
        cur.execute('delete from users')
        con.commit()
        con.close()

    @staticmethod
    async def user_exist(tel_id, loop):
        con, cur = await create_con(loop)
        await cur.execute('select count(*) from users where tel_id = %s', tel_id)
        r = await cur.fetchone()
        count = r[0]
        return count > 0

    @staticmethod
    async def get_user(tel_id, loop):
        con, cur = await create_con(loop)
        await cur.execute('select * from users where tel_id = %s', (tel_id))
        user = await cur.fetchone()
        con.close()

        if user is None:
            return None
        return User(user[0], user[1], user[2], user[3], user[4], user[5], user[6], user[7])

    @staticmethod
    def get_user_sync(tel_id):
        con, cur = create_sync_con()
        cur.execute('select * from users where tel_id = %s', tel_id)
        user = cur.fetchone()
        con.close()

        if user is None:
            return None

        return User(user[0], user[1], user[2], user[3], user[4], user[5], user[6], user[7])

    @staticmethod
    async def update_context(tel_id, context, loop):
        con, cur = await create_con(loop)
        await cur.execute('update users set context = %s where tel_id = %s', (context, tel_id))
        await con.commit()
        con.close()

    @staticmethod
    async def get_context(tel_id, loop):
        con, cur = await create_con(loop)
        await cur.execute('select context from users where tel_id = {0}'.format(tel_id))
        context = await cur.fetchone()
        con.close()
        return context[0]

    @staticmethod
    def sync_get_context(tel_id):
        con, cur = create_sync_con()
        cur.execute('select context from users where tel_id = {0}'.format(tel_id))
        context = cur.fetchone()
        con.close()

        if context is None:
            return None

        return context[0]

    @staticmethod
    async def get_all_users(loop):
        con, cur = await create_con(loop)
        await cur.execute('select * from users')
        users = await cur.fetchall()
        con.close()

        result = []
        for user in users:
            result.append(User(user[0], user[1], user[2], user[3], user[4], user[5], user[6], user[7]))
        return result

    @staticmethod
    async def create_user(phone, agent_id, loop):
        con, cur = await create_con(loop)
        await cur.execute("insert into users (context, phone, id_in_db) values (%s, %s, %s);", ('0', phone, agent_id))
        await con.commit()
        con.close()

    @staticmethod
    async def get_user_by_phone(phone, loop):
        con, cur = await create_con(loop)
        await cur.execute('select * from users where phone = %s', (phone))
        user = await cur.fetchone()
        con.close()

        if user is None:
            return None
        return User(user[0], user[1], user[2], user[3], user[4], user[5], user[6], user[7])

    @staticmethod
    async def get_user_by_agent_id(agent_id, loop):
        con, cur = await create_con(loop)
        await cur.execute('select * from users where id_in_db = %s', (agent_id))
        user = await cur.fetchone()
        con.close()

        if user is None:
            return None
        return User(user[0], user[1], user[2], user[3], user[4], user[5], user[6], user[7])

    @staticmethod
    async def block_user(phone, loop):
        con, cur = await create_con(loop)
        await cur.execute('update users set is_blocked = 1 where phone = %s', (phone))
        await con.commit()
        con.close()

    @staticmethod
    async def block_user_by_id(phone, loop):
        con, cur = await create_con(loop)
        await cur.execute('update users set is_blocked = 1 where id_in_db = %s', (phone))
        await con.commit()
        con.close()

    @staticmethod
    async def get_block(tel_id, loop):
        con, cur = await create_con(loop)
        await cur.execute('select * from users where tel_id = %s', (tel_id))
        user = await cur.fetchone()
        con.close()

        if user is None:
            return None
        return User(user[0], user[1], user[2], user[3], user[4], user[5], user[6], user[7])

    @staticmethod
    async def update_tel_id(tel_id, phone, loop):
        con, cur = await create_con(loop)
        await cur.execute('update users set tel_id = %s where phone = %s', (tel_id, phone))
        await con.commit()
        con.close()

    @staticmethod
    async def update_descr_by_phone(phone, descr, loop):
        con, cur = await create_con(loop)
        await cur.execute('update users set descr = %s where phone = %s', (descr, phone))
        await con.commit()
        con.close()

    @staticmethod
    async def get_all_active(loop):
        con, cur = await create_con(loop)
        await cur.execute('select * from users where is_blocked != 1 or is_blocked IS NULL')
        users = await cur.fetchall()
        con.close()

        result = []
        for user in users:
            result.append(User(user[0], user[1], user[2], user[3], user[4], user[5], user[6], user[7]))
        return result
