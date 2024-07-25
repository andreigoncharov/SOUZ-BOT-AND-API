import asyncio
import datetime
import re

import openpyxl
from openpyxl import Workbook
from openpyxl.styles import Alignment

from scripts.db_manager import RemoteDbManager

loop = asyncio.get_event_loop()


rdb = RemoteDbManager()


async def create_excel_file(expeditors, expeditor_names, customer_names):
    wb = Workbook()
    ws = wb.active
    row_counter = 1
    merge_rows = []
    for key, value in expeditors.items():
        ws.append([f"{re.sub(' +', ' ', str(expeditor_names.get(key)[0][0]).strip())} ({key})"])
        ws[f'A{row_counter}'].alignment = Alignment(horizontal='center', vertical='center')
        merge_rows.append(row_counter)
        row_counter += 1
        for order in value:
            ws.append([f"{re.sub(' +', ' ', str(customer_names.get(order[0])[0][1]).strip())}", order[1], order[2]])
            row_counter += 1
        ws.append([])
        row_counter += 1
    for col in ws.columns:
        max_length = 0
        column = col[0].column_letter
        for cell in col:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(cell.value)
            except:
                pass
        adjusted_width = (max_length + 2) * 2
        ws.column_dimensions[column].width = adjusted_width
    for index in merge_rows:
        ws.merge_cells(f'A{index}:C{index}')
    now = datetime.datetime.now()
    yesterday = now - datetime.timedelta(days=1)
    formatted_date = yesterday.strftime("%d-%m-%Y")
    wb.save(f"{formatted_date}.xlsx")


async def main():
    global rdb
    orders = await rdb.get_yesterday_docs(loop)
    if len(orders) > 0:
        expeditors = {}
        expeditor_names = {}
        customers = []
        customer_names = {}
        for order in orders:
            if order[0] not in expeditors:
                expeditors[order[0]] = []
            if order[1] not in customers:
                customers.append(order[1])
            expeditors[order[0]].append([order[1], order[2], order[3]])
        for expeditor in expeditors:
            expeditor_names[expeditor] = await rdb.get_expeditor_name(expeditor, loop)

        for key, value in expeditors.items():
            new_arr = []
            for ord in value:
                route = await rdb.get_point_by_dock(ord[1], loop)
                print(ord, route)
                new_arr.append([ord[0], ord[1], ord[2], route[0], route[1]])
            expeditors[key] = new_arr
        for customer in customers:
            customer_names[customer] = await rdb.get_customer_description(customer, loop)
        for key, value in expeditors.items():
            print(key, value)


expeditors = {'    9FSC ': [['SPO-049047', 'SPO0000495055', 'S'], ['SPO-044556', 'SPO0000494668', 'S'],
                            ['SPO-044556', 'SPO0000494869', 'S'], ['SPO-044556', 'SPO0000495049', 'S'],
                            ['SPO-044441', 'SPO0000491609', 'S'], ['SPO-044441', 'SPO0000494515', 'S'],
                            ['SPO-044837', 'SPO0000493808', 'S'], ['9900012067', 'SPO0000494379', 'S'],
                            ['9900012067', 'SPO0000494196', 'S']],
              '    DLSPO': [['A-199934324', 'SPO0000495527', 'S'], ['A-199934324', 'SPO0000494491', 'S'],
                            ['A-199934324', 'SPO0000494490', 'S'], ['A-199934324', 'SPO0000494298', 'S'],
                            ['A-199934324', 'SPO0000494296', 'S'], ['A-199934324', 'SPO0000493842', 'S'],
                            ['A-199934324', 'SPO0000493838', 'S'], ['8899999201', 'SPO0000494489', 'S']],
              '    7O   ': [['SPO-048632', 'SPO0000494144', 'S'], ['A-500004378', 'SPO0000493800', 'S'],
                            ['SPO-045201', 'SPO0000493353', 'S'], ['9999989910', 'SPO0000494271', 'S'],
                            ['9999989910', 'SPO0000494902', 'S'], ['9999989910', 'SPO0000494328', 'S'],
                            ['2277766000', 'SPO0000494027', 'S'], ['SPO-046780', 'SPO0000493748', 'S'],
                            ['SPO-0042376', 'SPO0000491431', 'S'], ['SPO-050290', 'SPO0000494428', 'S'],
                            ['SPO-046038', 'SPO0000493758', 'S'], ['SPO-046038', 'SPO0000491438', 'S'],
                            ['SPO-046038', 'SPO0000491422', 'S'], ['SPO-046244', 'SPO0000493760', 'S'],
                            ['SPO-045513', 'SPO0000493796', 'S']]}
expeditor_names = {'    9FSC ': [('Рудак                                   ',)],
                   '    DLSPO': [('Беззуб                                  ',)],
                   '    7O   ': [('Бакуменко                               ',)]}
customers = ['SPO-049047', 'SPO-044556', 'SPO-044441', 'SPO-044837', '9900012067', 'A-199934324', 'SPO-048632',
             'A-500004378', 'SPO-045201', '9999989910', '2277766000', 'SPO-046780', 'SPO-0042376', 'SPO-050290',
             'SPO-046038', 'SPO-046244', 'SPO-045513', '8899999201']
customer_names = {'SPO-049047': [('SPO-049047 ', '782 Кисет/Маяковского !!!!!                       ')],
                  'SPO-044556': [('SPO-044556 ', '859 Кисет/Артёма !!!!! !!!!!                      ')],
                  'SPO-044441': [('SPO-044441 ', 'Баскет 7/Алчевских                                ')],
                  'SPO-044837': [('SPO-044837 ', 'Баскет 11/Алчевских                               ')],
                  '9900012067': [('9900012067 ', 'Триняк/Гончара                                    ')],
                  'A-199934324': [('A-199934324', 'Пегарь Н.В/Южный                                  ')],
                  'SPO-048632': [('SPO-048632 ', 'Васильев/Барабашова                               ')],
                  'A-500004378': [('A-500004378', 'Пуляева /ТРЦ Барабашова ДР                        ')],
                  'SPO-045201': [('SPO-045201 ', 'Кофеин/Барабашово                                 ')],
                  '9999989910': [('9999989910 ', '57 Кисет/Якира !!!!! !!!!!                        ')],
                  '2277766000': [('2277766000 ', 'Шаверма/Барабашова                                ')],
                  'SPO-046780': [('SPO-046780 ', 'Алиев/Барабашово                                  ')],
                  'SPO-0042376': [('SPO-0042376', 'Арифния Реза/Барабашова                           ')],
                  'SPO-050290': [('SPO-050290 ', 'Хушвахтов/Барабашова                              ')],
                  'SPO-046038': [('SPO-046038 ', 'Яна/Барабашова                                    ')],
                  'SPO-046244': [('SPO-046244 ', 'Сердюк/Барабашово                                 ')],
                  'SPO-045513': [('SPO-045513 ', 'Камила/Барабашово                                 ')],
                  '8899999201': [('8899999201 ', 'Цепеленко/Южный/Октябрьская                       ')]}

asyncio.run(main())
# asyncio.run(create_excel_file(expeditors, expeditor_names, customer_names))
