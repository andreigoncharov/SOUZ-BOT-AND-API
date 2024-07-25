import asyncio

from scripts.db_manager import RemoteDbManager

loop = asyncio.get_event_loop()
rdb = RemoteDbManager()

expeditors = asyncio.run(rdb.get_yesterday_docs(loop))
print(expeditors)
