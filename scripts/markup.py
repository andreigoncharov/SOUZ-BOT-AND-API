from aiogram.types import reply_keyboard, inline_keyboard, ReplyKeyboardMarkup, KeyboardButton

phone_number = ReplyKeyboardMarkup(resize_keyboard=True). \
    add(KeyboardButton(text='Отправить номер телефона', request_contact=True))

ADMINS = [420404892, 301735028, 835344013]  #['AndreiGoncharov', 'maksym_hryhorovych']
LOW_ADMINS = [650989290, 5026697380, ]


def main_menu(tel_id):
    if tel_id not in ADMINS and tel_id not in LOW_ADMINS:
        return reply_keyboard.ReplyKeyboardMarkup([['ℹ️ Статусы доставки'], ['👥  Клиенты'], ['🚛 Экспедиторы']],
                                                  resize_keyboard=True)
    elif tel_id in ADMINS:
        return reply_keyboard.ReplyKeyboardMarkup(
            [['ℹ️ Статусы доставки'], ['👥  Клиенты'], ['🚛 Экспедиторы'], ['👑 Админ']],
            resize_keyboard=True)
    elif tel_id in LOW_ADMINS:
        return reply_keyboard.ReplyKeyboardMarkup([['🚛 Все экспедиторы'], ['📍 Последние чекины']],
                                                  resize_keyboard=True)


admin_menu = reply_keyboard.ReplyKeyboardMarkup(
    [['✅ Добавить агента'], ['⛔️ Исключить агента'], ['🚛 Все экспедиторы'], ['📍 Последние чекины'],
    ['⬅️ Главное меню']],
    resize_keyboard=True)

cancel = reply_keyboard.ReplyKeyboardMarkup([['❌ Отменить']],
                                            resize_keyboard=True)


def search_keyboard():
    keyboard = inline_keyboard.InlineKeyboardMarkup()
    clients = inline_keyboard.InlineKeyboardButton('👥 Поиск клиента', callback_data='search_clients')
    expeditors = inline_keyboard.InlineKeyboardButton('🚛 Поиск экспедитора', callback_data='search_expeditors')
    keyboard.add(clients)
    keyboard.add(expeditors)
    return keyboard


def promocode_yes_no():
    keyboard = inline_keyboard.InlineKeyboardMarkup()
    yes = inline_keyboard.InlineKeyboardButton('Так', callback_data=f'promocode_yes')
    no = inline_keyboard.InlineKeyboardButton('Ні', callback_data=f'promocode_no')
    keyboard.add(yes)
    keyboard.add(no)
    return keyboard
