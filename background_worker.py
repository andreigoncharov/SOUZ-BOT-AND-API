import asyncio
import datetime

from scripts.db_manager import RemoteDbManager

loop = asyncio.get_event_loop()
rdb = RemoteDbManager()

async def main():
    global rdb
    orders = await rdb.get_yesterday_docs(loop)
    # orders = [('SPO-045487', 'SPO0000489781', 'SA', datetime.datetime(2024, 7, 24, 17, 14, 53, 693000)), ('8889885799', 'SPO0000492667', 'SA', datetime.datetime(2024, 7, 24, 17, 23, 22, 890000)), ('9989988643', 'SPO0000490075', 'SA', datetime.datetime(2024, 7, 24, 17, 20, 0, 820000)), ('A-500006303', 'SPO0000492691', 'R', datetime.datetime(2024, 7, 24, 17, 24, 55, 547000)), ('A-500003174', 'SPO0000493076', 'R', datetime.datetime(2024, 7, 24, 17, 13, 36, 983000)), ('A-500006304', 'SPO0000491247', 'R', datetime.datetime(2024, 7, 24, 17, 17, 34, 287000)), ('SPO-047725', 'SPO0000492714', 'S', datetime.datetime(2024, 7, 24, 17, 26, 16, 510000)), ('A-500003136', 'SPO0000493079', 'S', datetime.datetime(2024, 7, 24, 17, 24, 5, 507000)), ('A-500003136', 'SPO0000493080', 'S', datetime.datetime(2024, 7, 24, 17, 24, 5, 507000)), ('A-500005675', 'SPO0000492735', 'SA', datetime.datetime(2024, 7, 24, 17, 25, 29, 253000)), ('A-500003038', 'SPO0000492499', 'R', datetime.datetime(2024, 7, 24, 17, 21, 56, 420000)), ('A-500003038', 'SPO0000493042', 'R', datetime.datetime(2024, 7, 24, 17, 21, 56, 420000)), ('SPO-045198', 'SPO0000492736', 'R', datetime.datetime(2024, 7, 24, 17, 14, 40, 107000)), ('9999995810', 'SPO0000491923', 'R', datetime.datetime(2024, 7, 24, 17, 25, 46, 950000)), ('8888899860', 'SPO0000492506', 'S', datetime.datetime(2024, 7, 24, 17, 25, 12, 353000)), ('8888899860', 'SPO0000493084', 'S', datetime.datetime(2024, 7, 24, 17, 25, 12, 353000)), ('SPO-0043744', 'SPO0000491226', 'S', datetime.datetime(2024, 7, 24, 17, 19, 31, 270000)), ('SPO-047165', 'SPO0000493039', 'S', datetime.datetime(2024, 7, 24, 17, 26, 56, 47000)), ('SPO-047165', 'SPO0000492490', 'S', datetime.datetime(2024, 7, 24, 17, 26, 56, 47000)), ('SPO-047165', 'SPO0000493037', 'S', datetime.datetime(2024, 7, 24, 17, 26, 56, 47000)), ('SPO-047165', 'SPO0000491560', 'S', datetime.datetime(2024, 7, 24, 17, 26, 56, 47000)), ('SPO-047684', 'SPO0000492485', 'S', datetime.datetime(2024, 7, 24, 17, 14, 16, 597000)), ('SPO-047684', 'SPO0000493027', 'S', datetime.datetime(2024, 7, 24, 17, 14, 16, 597000))]
    if len(orders) > 0:
        expeditors = {}
        expeditor_names = {}
        for order in orders:
            if order[0] not in expeditors:
                expeditors[order[0]] = []
            expeditors[order[0]].append([order[1], order[2]])
        for ex in expeditors:
            expeditor_names[ex] = await rdb.get_expeditor_name(ex, loop)
        print(expeditor_names)

asyncio.run(main())