start_text_new_user = '''Добро пожаловать!

Для получения доступа для работы с чат-боту сообщите Ваш номер телефона администратору. 

После того, как администратор добавит Вас в чат-бот, нажмите кнопку "Отправить номер телефона"
'''

start_text_new_user_2 = '''У Вас еще нет доступа к чат-боту!

Для получения доступа для работы с чат-боту сообщите Ваш номер телефона администратору. 

После того, как администратор добавит Вас в чат-бот, нажмите кнопку "Отправить номер телефона"
'''

start_text = '''Добро пожаловать!'''

user_not_exists = '''⛔️ ⛔️ ⛔️
 
В настоящее время у Вас нет доступа! 

Обратитесь к администратору для получения доступа!

⛔️ ⛔️ ⛔️'''


no_admin_text = '''⛔️ ⛔️ ⛔️

Этот функционал доступен только администратору!

⛔️ ⛔️ ⛔️
'''

no_clients_today = 'Сегодня нет доставок Вашим клиентам!'

clients_list = 'Список Ваших клиентов, у на сегодня запланированна доставка:'

expeditors_list = 'Список экспедиторов, которые сегодня доставляют Вашим клиентам:'

choose_search = 'Выберите категорию для поиска:'

client_header = '''👤 Клиент: {0}\n'''
client_header_html = '''👤 <u><b>Клиент:</b></u> {0}\n'''

order_header = '''🪧 Номер заказа: {0}\n'''
order_header_html = '''🪧 <b>Номер заказа:</b> {0}\n'''

expeditor_header = '''🚛 Экспедитор: {0}\n'''

driver_header = '''🚚 <b>Водитель:</b> {0}\n'''

route_header = '''🛣️ Маршрут: {0}'''
route_header_html = '''🛣️ <u><b>Маршрут:</b></u> {0}'''
number_header = '''📍<b>Номер в подрядке отгрузки:</b> {0}'''
last_checkin = '''📑 <b>Последний чекин экспедитора:</b> {0}'''

shipped_status_text = '''🟢 <b>Статус:</b> Отгружен'''
on_way_status_text = '''🟡 <b>Статус:</b> В пути'''
shipped_with_adjustment_status_text = '''🟠 <b>Статус:</b> Отгружен c корректировкой'''
refused_status_text = '''🔴 <b>Статус:</b> Отказ'''

client_shipped_text = '''
🟢 <b>Статус:</b> Отгружен
🕓 <b>Дата и время отгрузки:</b> {0}

'''

client_on_way_text = '''
📍<b>Номер в подрядке отгрузки:</b> {0}
📑 <b>Последний чекин экспедитора:</b> {1}

🟡 <b>Статус:</b> В пути
'''

client_shipped_with_adjustment_text = '''
🟠 <b>Статус:</b> Отгружен c корректировкой
🕓 <b>Дата и время отгрузки:</b> {0}

'''

client_refused_text = '''
🔴 <b>Статус:</b> Отказ
🕓 <b>Дата и время отказа:</b> {0}

'''

expeditor_client_shipped_text = '''🟢 {0} (точка {1}) - отгружен'''
expeditor_client_shipped_with_adjustment_text = '''🟠 {0} (точка {1}) - отгружен с корректировкой'''
expeditor_client_refused_text = '''🔴 {0} (точка {1}) - отказ'''
expeditor_client_on_way_text = '''🟡 {0} (точка {1}) - в пути'''


clients_shipped_text = '''🟢 {0} - отгружен'''
clients_shipped_with_adjustment_text = '''🟠 {0} - отгружен с корректировкой'''
clients_refused_text = '''🔴 {0} - отказ'''
clients_on_way_text = '''🟡 {0} - в пути'''


''' АДМИН '''

enter_phone = '''Введите номер телефона в формате:

 <b>380999999999</b>'''

not_correct_phone_format = '''⛔ Некорретный номер телефона! Введите номер телефона в формате:

<b>380999999999</b>'''