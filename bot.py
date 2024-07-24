import re
import re
import traceback
import uuid

from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InputTextMessageContent, InlineQueryResultArticle, InlineKeyboardMarkup, InlineKeyboardButton, \
    Message

import scripts.markup as mk
import scripts.messages as msg
from scripts.db_manager import *

loop = asyncio.get_event_loop()

bot = Bot(TOKEN)
dp = Dispatcher(bot)

# if DEBUG:
#     logging.basicConfig(level=logging.DEBUG)

ADMINS = [420404892, 650989290, 301735028, 5026697380]#['AndreiGoncharov', 'maksym_hryhorovych']

PHONE_MASK = re.compile(r'^380\d{9}$')

RDB = RemoteDbManager()

'''Старт и регистрация'''


@dp.message_handler(commands=['start'])
async def start(message: Message):
    tel_id = message.chat.id
    if not await UsersDbManager.user_exist(tel_id, loop):
        text = msg.start_text_new_user
        await bot.send_message(tel_id, text, reply_markup=mk.phone_number,
                               disable_notification=True, parse_mode='html')
        return
    user = await UsersDbManager.get_user(tel_id, loop)
    print(user.is_blocked)
    if user.is_blocked == 1 or user.is_blocked == True:
        text = msg.user_not_exists
        await bot.send_message(tel_id, text,
                               disable_notification=True, parse_mode='html')
        return
    await bot.send_message(tel_id, msg.start_text, reply_markup=mk.main_menu(tel_id in ADMINS),
                           disable_notification=True, parse_mode='html')


@dp.message_handler(content_types=types.ContentType.CONTACT)
async def handle_contact(message: types.Message):
    phone_number = message.contact.phone_number
    tel_id = message.chat.id
    phone_number = normalize_phone_number(phone_number)
    user = await UsersDbManager.get_user_by_phone(phone_number, loop)
    if user is not None:
        if user.is_blocked == 1:
            text = msg.user_not_exists
            await bot.send_message(tel_id, text,
                                   disable_notification=True, parse_mode='html')
            return
        else:
            await UsersDbManager.update_tel_id(tel_id, phone_number, loop)
            await bot.send_message(tel_id, msg.start_text,
                                   reply_markup=mk.main_menu(tel_id in ADMINS),
                                   disable_notification=True, parse_mode='html')
    else:
        text = msg.start_text_new_user_2
        await bot.send_message(tel_id, text, reply_markup=mk.phone_number,
                               disable_notification=True, parse_mode='html')
        return


'''Поиск клиентов'''


@dp.message_handler(lambda message: message.text == '👥  Клиенты')
async def c_list_def(message):
    tel_id = message.chat.id
    user = await UsersDbManager.get_user(tel_id, loop)
    if user.is_blocked:
        text = msg.user_not_exists
        await bot.send_message(tel_id, text,
                               disable_notification=True, parse_mode='html')
        return
    text = 'Поиск информации...'
    mess = await bot.send_message(tel_id, text,
                                  disable_notification=True, parse_mode='html')
    clients = await RDB.get_client_names(user.id_in_db, loop)
    await bot.delete_message(tel_id, mess.message_id)

    if len(clients) > 1:
        sorted_clients = []
        for client in clients:
            if not any(sublist[0] == client[0] for sublist in sorted_clients):
                sorted_clients.append([client[0], client[1], [client]])
            else:
                for c in sorted_clients:
                    if c[0] == client[0]:
                        c[2].append(client)
                        break
        keyb = InlineKeyboardMarkup()
        for client in sorted_clients:
            keyb.add(
                InlineKeyboardButton(client[1], callback_data=f"cmi*{re.sub(' +', ' ', str(client[0]).strip())}"))
        await bot.send_message(tel_id, msg.clients_list, reply_markup=keyb,
                               disable_notification=True, parse_mode='html')
    else:
        await bot.send_message(tel_id, msg.no_clients_today,
                               disable_notification=True, parse_mode='html')


@dp.inline_handler(lambda inline_query: inline_query.query.startswith('search_clients'))
async def show_zn_inl(inline_query):
    tel_id = inline_query.from_user.id
    user = await UsersDbManager.get_user(tel_id, loop)
    text = 'Поиск информации...'
    mess = await bot.send_message(tel_id, text,
                                  disable_notification=True, parse_mode='html')
    clients = await RDB.get_clients(user.id_in_db, loop)
    await bot.delete_message(tel_id, mess.message_id)
    # expeditors_and_routes = await RDB.get_unique_expeditor_routes_by_agent(AGENT, loop)
    sorted_clients = []
    expeditor_routes = []
    for client in clients:
        if not any(sublist[0] == client[0] for sublist in sorted_clients):
            sorted_clients.append([client[0], client[1], [client]])
        else:
            for c in sorted_clients:
                if c[0] == client[0]:
                    c[2].append(client)
                    break
        if client[2] not in expeditor_routes:
            expeditor_routes.append(client[2])
    # last_checkins = await RDB.get_expeditor_last_checkin(', '.join([f"'{id}'" for id in expeditor_routes]), loop)
    # print(last_checkins)

    if len(sorted_clients) == 0:
        result_id = str(uuid.uuid4())
        message_content = InputTextMessageContent(msg.no_clients_today)
        result = InlineQueryResultArticle(
            id=result_id, title=msg.no_clients_today,
            thumb_url='https://img.icons8.com/dotty/2x/nothing-found.png',
            thumb_height=400, thumb_width=400,
            input_message_content=message_content
        )
        await bot.answer_inline_query(inline_query.id, results=[result], cache_time=1)
        return

    if inline_query.offset != '':
        offset = int(inline_query.offset)
    else:
        offset = 0

    if len(sorted_clients) < offset + len(sorted_clients):
        next_offset = ''
        end = len(sorted_clients)
    else:
        next_offset = offset + len(sorted_clients)
        end = next_offset

    results = []
    for i in range(offset, end):
        client = sorted_clients[i]
        try:
            image_url = None
            result_id = str(uuid.uuid4())

            item_description = msg.client_header.format(f"{re.sub(' +', ' ', str(client[1]).strip())}", )
            for order in client[2]:
                order_text = f'''
{msg.route_header.format(str(order[6]))}
'''
                if order[7] is not None:
                    if order[8] == 'S' or order[8] is None:
                        order_text += msg.shipped_status_text
                    elif order[8] == 'SA':
                        order_text += msg.shipped_with_adjustment_status_text
                    else:
                        order_text += msg.client_refused_text
                else:
                    order_text += msg.on_way_status_text

                item_description += order_text + "\n--------\n"
            message_content = InputTextMessageContent(item_description, parse_mode='html')
            keyb = InlineKeyboardMarkup()
            keyb.add(
                InlineKeyboardButton("ℹ️ Подробнее", callback_data=f"cmi*{re.sub(' +', ' ', str(client[0]).strip())}"))
        # except KeyError:
        #     continue
        except Exception:
            print(traceback.format_exc())
            continue

        results.append(
            InlineQueryResultArticle(
                id=result_id, title=item_description,
                thumb_url=image_url,
                thumb_height=400, thumb_width=400,
                input_message_content=message_content,
                reply_markup=keyb
            ))
    try:
        await bot.answer_inline_query(inline_query.id, results=results, next_offset=str(next_offset), cache_time=1)
    except Exception as e:
        print(traceback.format_exc())


@dp.callback_query_handler(lambda call: call.data.startswith('cmi*'))
async def choose_language(call: types.CallbackQuery):
    tel_id = call.from_user.id
    user = await UsersDbManager.get_user(tel_id, loop)
    if user.is_blocked:
        text = msg.user_not_exists
        await bot.send_message(tel_id, text,
                               disable_notification=True, parse_mode='html')
        return
    callback_data = call.data.split('*')[-1]
    text = 'Поиск информации...'
    mess = await bot.send_message(tel_id, text,
                                  disable_notification=True, parse_mode='html')
    orders = await RDB.get_client_info(callback_data, loop)
    await bot.delete_message(tel_id, mess.message_id)
    item_description = msg.client_header.format(f"{re.sub(' +', ' ', str(orders[0][1]).strip())} ")
    exped = []
    for order in orders:
        order_text = f'''
{msg.expeditor_header.format(
            f"{re.sub(' +', ' ', str(order[3]).strip())}", )}
{msg.driver_header.format(
            f"{re.sub(' +', ' ', str(order[5]).strip())}", )}    
{msg.route_header.format(str(order[6]))}
    '''
        if order[7] is not None:
            if order[8] == 'S' or order[8] is None:
                order_text += msg.client_shipped_text.format(order[7].strftime("%d-%m-%Y %H:%M"))
            elif order[8] == 'SA':
                order_text += msg.client_shipped_with_adjustment_text.format(order[7].strftime("%d-%m-%Y %H:%M"))
            else:
                order_text += msg.client_refused_text.format(
                    order[7].strftime("%d-%m-%Y %H:%M"))
        else:
            # last_checkin = await RDB.get_expeditor_last_checkin(order[2], order[6], loop)
            if exped == []:
                xl = await RDB.get_expeditor_clients(order[2], loop)
                last_checkin = find_last_checkin(xl, order[2])
                exped.append([order[2], xl])
            else:
                is_in = False
                for exp in exped:
                    if exp[0] == order[2]:
                        last_checkin = find_last_checkin(exp[1], order[2])
                        is_in = True
                        break
                if not is_in:
                    xl = await RDB.get_expeditor_clients(order[2], loop)
                    last_checkin = find_last_checkin(xl, order[2])
                    exped.append([order[2], xl])
            order_text += msg.client_on_way_text.format(order[9],
                                                        f"точка {last_checkin[0]} в {last_checkin[1].split()[1][:5] if last_checkin[1] != 'None' else '-----'}"
                                                        if last_checkin != -1 else '-----')
        item_description += order_text + "\n--------\n"
    # await bot.send_message(tel_id, item_description, parse_mode='html', disable_notification=True)
    keyb = InlineKeyboardMarkup()
    keyb.add(
        InlineKeyboardButton("⬅️ Список клиентов", callback_data=f"clients_back"))
    await bot.edit_message_text(item_description, tel_id, call.message.message_id, parse_mode='html', reply_markup=keyb)


@dp.callback_query_handler(lambda call: call.data.startswith('clients_back'))
async def choose_language(call: types.CallbackQuery):
    tel_id = call.from_user.id
    user = await UsersDbManager.get_user(tel_id, loop)
    if user.is_blocked:
        text = msg.user_not_exists
        await bot.send_message(tel_id, text,
                               disable_notification=True, parse_mode='html')
        return
    text = 'Поиск информации...'
    mess = await bot.send_message(tel_id, text,
                                  disable_notification=True, parse_mode='html')
    clients = await RDB.get_client_names(user.id_in_db, loop)
    await bot.delete_message(tel_id, mess.message_id)
    if len(clients) > 1:
        sorted_clients = []
        for client in clients:
            if not any(sublist[0] == client[0] for sublist in sorted_clients):
                sorted_clients.append([client[0], client[1], [client]])
            else:
                for c in sorted_clients:
                    if c[0] == client[0]:
                        c[2].append(client)
                        break
        keyb = InlineKeyboardMarkup()
        for client in sorted_clients:
            keyb.add(
                InlineKeyboardButton(client[1], callback_data=f"cmi*{re.sub(' +', ' ', str(client[0]).strip())}"))
        await bot.edit_message_text(msg.clients_list, tel_id, call.message.message_id, reply_markup=keyb,
                                    parse_mode='html')
    else:
        await bot.edit_message_text(msg.no_clients_today, tel_id, call.message.message_id,
                                    parse_mode='html')


''' Поиск экспедиторов'''


@dp.message_handler(lambda message: message.text == '🚛 Экспедиторы')
async def c_list_def(message):
    tel_id = message.chat.id
    user = await UsersDbManager.get_user(tel_id, loop)
    if user.is_blocked:
        text = msg.user_not_exists
        await bot.send_message(tel_id, text,
                               disable_notification=True, parse_mode='html')
        return
    text = 'Поиск информации...'
    mess = await bot.send_message(tel_id, text,
                                  disable_notification=True, parse_mode='html')

    clients = await RDB.get_all_expeditors(user.id_in_db, loop)
    await bot.delete_message(tel_id, mess.message_id)
    if len(clients) > 0:
        sorted_clients = []
        for client in clients:
            if not any(sublist[0] == client[0] for sublist in sorted_clients):
                sorted_clients.append([client[0], client[1], [client]])
            else:
                for c in sorted_clients:
                    if c[0] == client[0]:
                        c[2].append(client)
                        break
        keyb = InlineKeyboardMarkup()
        for client in sorted_clients:
            keyb.add(
                InlineKeyboardButton(client[1], callback_data=f"emi*{re.sub(' +', ' ', str(client[0]).strip())}"))
        await bot.send_message(tel_id, msg.clients_list, reply_markup=keyb, parse_mode='html',
                               disable_notification=True)
    else:
        await bot.send_message(tel_id, msg.no_clients_today,
                               reply_markup=mk.main_menu(tel_id in ADMINS), parse_mode='html',
                               disable_notification=True)


@dp.inline_handler(lambda inline_query: inline_query.query.startswith('search_expeditors'))
async def show_zn_inl(inline_query):
    tel_id = inline_query.from_user.id
    user = await UsersDbManager.get_user(tel_id, loop)
    text = 'Поиск информации...'
    mess = await bot.send_message(tel_id, text,
                                  disable_notification=True, parse_mode='html')
    clients = await RDB.get_all_expeditors(user.id_in_db, loop)
    await bot.delete_message(tel_id, mess.message_id)

    if len(clients) == 0:
        result_id = str(uuid.uuid4())
        message_content = InputTextMessageContent(msg.no_clients_today)
        result = InlineQueryResultArticle(
            id=result_id, title=msg.no_clients_today,
            thumb_url='https://img.icons8.com/dotty/2x/nothing-found.png',
            thumb_height=400, thumb_width=400,
            input_message_content=message_content
        )
        await bot.answer_inline_query(inline_query.id, results=[result], cache_time=1)
        return

    if inline_query.offset != '':
        offset = int(inline_query.offset)
    else:
        offset = 0

    if len(clients) < offset + len(clients):
        next_offset = ''
        end = len(clients)
    else:
        next_offset = offset + len(clients)
        end = next_offset

    results = []
    for i in range(offset, end):
        client = clients[i]
        try:
            image_url = None
            result_id = str(uuid.uuid4())

            item_description = msg.expeditor_header.format(f"{re.sub(' +', ' ', str(client[1]).strip())}")
            message_content = InputTextMessageContent(item_description, parse_mode='html')
            keyb = InlineKeyboardMarkup()
            keyb.add(
                InlineKeyboardButton("👥 Список клиентов",
                                     callback_data=f"emi*{re.sub(' +', ' ', str(client[0]).strip())}"))
        except KeyError:
            continue

        results.append(
            InlineQueryResultArticle(
                id=result_id, title=item_description,
                thumb_url=image_url,
                thumb_height=400, thumb_width=400,
                input_message_content=message_content,
                reply_markup=keyb
            ))
    try:
        await bot.answer_inline_query(inline_query.id, results=results, next_offset=str(next_offset), cache_time=1)
    except:
        print('Network error, file too large')


@dp.callback_query_handler(lambda call: call.data.startswith('emi*'))
async def choose_language(call: types.CallbackQuery):
    tel_id = call.from_user.id
    user = await UsersDbManager.get_user(tel_id, loop)
    if user.is_blocked:
        text = msg.user_not_exists
        await bot.send_message(tel_id, text,
                               disable_notification=True, parse_mode='html')
        return
    expeditor_id = call.data.split('*')[-1]
    text = 'Поиск информации...'
    mess = await bot.send_message(tel_id, text,
                                  disable_notification=True, parse_mode='html')

    clients = await RDB.get_expeditor_clients_by_agent(user.id_in_db, expeditor_id, loop)
    text = msg.expeditor_header_with_phone.format(
        f"{re.sub(' +', ' ', str(clients[0][0]).strip())}", normalize_phone_number_plus(str(clients[0][7])))
    routes = []
    points = []
    for client in clients:
        if client[3] not in routes:
            if routes != []:
                text += '\n ---------- \n '
            # last_checkin = await RDB.get_expeditor_last_checkin(expeditor_id, client[3], loop)
            last_checkin = find_last_checkin(clients, client[3])
            text += f'\n {msg.route_header_html.format(client[3])} \n '
            text += f'''\n {msg.last_checkin.format(f"точка {last_checkin[0]} в {last_checkin[1].split()[1][:5]}"
                                                    if last_checkin != -1 else '-----')} \n '''
            if is_all_points(clients, client[3]):
                text += f'\n {msg.all_points_complete} \n '
            routes.append(client[3])
        client_name = re.sub(' +', ' ', str(client[2]).strip())
        # client_id = re.sub(' +', ' ', str(client[3]).strip())
        if client[4] not in points:
            points.append(client[4])
            if client[5] is not None:
                if client[6] == 'S' or client[6] is None:
                    text += '\n' + msg.expeditor_client_shipped_text.format(client_name, client[4],
                                                                            str(client[5]).split()[1][:5]) + '\n '
                elif client[6] == 'SA':
                    text += '\n' + msg.expeditor_client_shipped_with_adjustment_text.format(client_name, client[4],
                                                                                            str(client[5]).split()[1][
                                                                                            :5]) + '\n '
                else:
                    text += '\n' + msg.expeditor_client_refused_text.format(client_name, client[4],
                                                                            str(client[5]).split()[1][:5]) + '\n '
            else:
                text += '\n' + msg.expeditor_client_on_way_text.format(client_name, client[4]) + '\n '
    keyb = InlineKeyboardMarkup()
    keyb.add(
        InlineKeyboardButton("⬅️ Список экспедиторов", callback_data=f"expeditors_back"))
    res_text = split_message(text)
    if len(res_text) == 1:
        await bot.delete_message(tel_id, mess.message_id)
        await bot.edit_message_text(res_text[0], tel_id, call.message.message_id, parse_mode='html', reply_markup=keyb)
    else:
        for t in res_text:
            if t != res_text[len(res_text) - 1]:
                await bot.delete_message(tel_id, mess.message_id)
                await bot.send_message(tel_id, t, parse_mode='html')
            else:
                await bot.delete_message(tel_id, mess.message_id)
                await bot.send_message(tel_id, t, parse_mode='html', reply_markup=keyb)


@dp.callback_query_handler(lambda call: call.data.startswith('expeditors_back'))
async def choose_language(call: types.CallbackQuery):
    tel_id = call.from_user.id
    user = await UsersDbManager.get_user(tel_id, loop)
    if user.is_blocked:
        text = msg.user_not_exists
        await bot.send_message(tel_id, text,
                               disable_notification=True, parse_mode='html')
        return

    clients = await RDB.get_all_expeditors(user.id_in_db, loop)
    if len(clients) > 1:
        sorted_clients = []
        for client in clients:
            if not any(sublist[0] == client[0] for sublist in sorted_clients):
                sorted_clients.append([client[0], client[1], [client]])
            else:
                for c in sorted_clients:
                    if c[0] == client[0]:
                        c[2].append(client)
                        break
        keyb = InlineKeyboardMarkup()
        for client in sorted_clients:
            keyb.add(
                InlineKeyboardButton(client[1], callback_data=f"emi*{re.sub(' +', ' ', str(client[0]).strip())}"))
        await bot.edit_message_text(msg.clients_list, tel_id, call.message.message_id, reply_markup=keyb,
                                    parse_mode='html')
    else:
        await bot.edit_message_text(msg.no_clients_today, tel_id, call.message.message_id,
                                    parse_mode='html')


'''Статусы доставки'''


@dp.message_handler(lambda message: message.text == 'ℹ️ Статусы доставки')
async def reff_link(message):
    tel_id = message.chat.id
    user = await UsersDbManager.get_user(tel_id, loop)
    if user.is_blocked:
        text = msg.user_not_exists
        await bot.send_message(tel_id, text,
                               disable_notification=True, parse_mode='html')
        return
    text = 'Поиск информации...'
    mess = await bot.send_message(tel_id, text,
                                  disable_notification=True, parse_mode='html')

    clients = await RDB.get_clients(user.id_in_db, loop)
    await bot.delete_message(tel_id, mess.message_id)

    if len(clients) > 0:
        text = ''
        clients_shipped = []
        clients_shipped_with_adjustment = []
        clients_refused = []
        clients_on_way = []

        for client in clients:
            client_name = re.sub(' +', ' ', str(client[1]).strip())
            # client_id = re.sub(' +', ' ', str(client[0]).strip())
            if client[7] is not None:
                if client[8] == 'S' or client[8] is None:
                    clients_shipped.append((client_name))
                elif client[8] == 'SA':
                    clients_shipped_with_adjustment.append((client_name))
                else:
                    clients_refused.append((client_name))
            else:
                clients_on_way.append((client_name))

        all_clients = clients_shipped + clients_shipped_with_adjustment + clients_refused + clients_on_way

        text = ''
        for client_name in all_clients:
            if (client_name) in clients_shipped:
                text += '\n' + msg.clients_shipped_text.format(client_name) + '\n '
            elif (client_name) in clients_shipped_with_adjustment:
                text += '\n' + msg.clients_shipped_with_adjustment_text.format(client_name) + '\n '
            elif (client_name) in clients_refused:
                text += '\n' + msg.clients_refused_text.format(client_name) + '\n '
            else:
                text += '\n' + msg.clients_on_way_text.format(client_name) + '\n '

    else:
        text = msg.no_clients_today

    await bot.send_message(tel_id, text, reply_markup=mk.main_menu(tel_id in ADMINS),
                           disable_notification=True, parse_mode='html')


'''Админ'''


@dp.message_handler(lambda message: message.text == '👑 Админ')
async def reff_link(message):
    tel_id = message.chat.id
    # if tel_id not in ADMINS:
    #     await bot.send_message(tel_id, msg.no_admin_text,
    #                            disable_notification=True, parse_mode='html')
    #     return
    text = 'Меню администратора'
    await bot.send_message(tel_id, text, reply_markup=mk.admin_menu,
                           disable_notification=True, parse_mode='html')


@dp.message_handler(lambda message: message.text == '⬅️ Главное меню')
async def reff_link(message):
    tel_id = message.chat.id
    text = 'Главное меню'
    await bot.send_message(tel_id, text, reply_markup=mk.main_menu(tel_id in ADMINS),
                           disable_notification=True, parse_mode='html')


@dp.message_handler(lambda message: message.text == '❌ Отменить')
async def reff_link(message):
    tel_id = message.chat.id
    text = 'Операция отменена!'
    await UsersDbManager.update_context(tel_id, 0, loop)
    await bot.send_message(tel_id, text, reply_markup=mk.admin_menu,
                           disable_notification=True, parse_mode='html')


@dp.callback_query_handler(lambda call: call.data.startswith('cancel_search'))
async def choose_language(call: types.CallbackQuery):
    tel_id = call.from_user.id
    text = 'Операция отменена!'
    await UsersDbManager.update_context(tel_id, 0, loop)
    await bot.send_message(tel_id, text, reply_markup=mk.admin_menu,
                           disable_notification=True, parse_mode='html')


@dp.message_handler(lambda message: message.text == '✅ Добавить агента')
async def reff_link(message):
    tel_id = message.chat.id
    # if tel_id not in ADMINS:
    #     await bot.send_message(tel_id, msg.no_admin_text,
    #                            disable_notification=True, parse_mode='html')
    #     return
    text = msg.enter_surname
    await bot.send_message(tel_id, text, reply_markup=mk.cancel,
                           disable_notification=True, parse_mode='html')
    await UsersDbManager.update_context(tel_id, 'wait_agent_surname', loop)


@dp.message_handler(lambda message: UsersDbManager.sync_get_context(message.chat.id) == 'wait_agent_surname',
                    content_types=['text'])
async def seller_registration_wait_patronymic(message):
    tel_id = message.chat.id
    if len(message.text) > 2:
        text = 'Поиск агента ...'
        mess = await bot.send_message(tel_id, text,
                                      disable_notification=True, parse_mode='html')
        res = await RDB.search_agent_by_description(message.text, loop)
        await bot.delete_message(tel_id, mess.message_id)
        if len(res) > 0:
            text = 'Найденные агенты:'
            keyb = InlineKeyboardMarkup()
            for agent in res:
                name = re.sub(' +', ' ', str(agent[1]).strip())
                ag_id = re.sub(' +', ' ', str(agent[0]).strip())
                uex = await UsersDbManager.get_user_by_agent_id(ag_id, loop)
                if uex is not None:
                    keyb.add(
                        InlineKeyboardButton(f"✅ {name} ({ag_id})",
                                             callback_data=f"agentaddalreadyexists*{ag_id}"))
                else:
                    keyb.add(
                        InlineKeyboardButton(f"{name} ({ag_id})",
                                             callback_data=f"agentadd*{ag_id}"))
            keyb.add(
                InlineKeyboardButton("❌ Отменить",
                                     callback_data=f"cancel_search"))
            await bot.send_message(tel_id, text, reply_markup=keyb,
                                   disable_notification=True, parse_mode='html')
        else:
            text = f'Агент с фамилией {message.text} не найден в базе!'
            await bot.send_message(tel_id, text, reply_markup=mk.cancel,
                                   disable_notification=True, parse_mode='html')
    else:
        text = 'Введите не менее двух символов!'
        await bot.send_message(tel_id, text, reply_markup=mk.cancel,
                               disable_notification=True, parse_mode='html')


@dp.callback_query_handler(lambda call: call.data.startswith('agentaddalreadyexists*'))
async def choose_language(call: types.CallbackQuery):
    tel_id = call.from_user.id
    agent_id = call.data.split('*')[-1]
    user = await UsersDbManager.get_user_by_agent_id(agent_id, loop)
    text = f'❗️Данный агент уже зарегестрирован в боте!\n \n {user.descr} ({user.id_in_db})\n {user.phone}'
    await bot.send_message(tel_id, text, reply_markup=mk.cancel,
                           disable_notification=True, parse_mode='html')


@dp.callback_query_handler(lambda call: call.data.startswith('agentadd*'))
async def choose_language(call: types.CallbackQuery):
    tel_id = call.from_user.id
    agent_id = call.data.split('*')[-1]
    text = msg.enter_phone
    await bot.send_message(tel_id, text, reply_markup=mk.cancel,
                           disable_notification=True, parse_mode='html')
    await UsersDbManager.update_context(tel_id, f'wait_phone_number-{agent_id}', loop)


@dp.message_handler(lambda message: UsersDbManager.sync_get_context(message.chat.id).startswith('wait_phone_number'),
                    content_types=['text'])
async def seller_registration_wait_patronymic(message):
    tel_id = message.chat.id
    agent_id = await UsersDbManager.get_context(tel_id, loop)
    agent_id = agent_id.split('-')[-1]
    phone_number = message.text
    if not PHONE_MASK.match(message.text):
        await bot.send_message(tel_id, msg.not_correct_phone_format, disable_notification=True, parse_mode='html')
        return
    if await UsersDbManager.get_user_by_phone(message.text, loop) is not None:
        text = 'Данный номер телефона уже зарегестрирован в базе!'
        await bot.send_message(tel_id, text, reply_markup=mk.admin_menu,
                               disable_notification=True, parse_mode='html')
        await UsersDbManager.update_context(tel_id, f'0', loop)
        return
    agent_descr = await RDB.get_agent_description(agent_id, loop)
    await UsersDbManager.create_user(phone_number, agent_id, loop)
    await UsersDbManager.update_descr_by_phone(phone_number, re.sub(' +', ' ', str(agent_descr[0][1]).strip()),
                                               loop)
    await UsersDbManager.update_context(tel_id, '0', loop)
    text = f"Агент <b><u>{re.sub(' +', ' ', str(agent_descr[0][1]).strip())}({message.text})</u></b> " \
           f"с номером телефона <b><u>{phone_number}</u></b> добавлен!"
    await bot.send_message(tel_id, text, reply_markup=mk.admin_menu,
                           disable_notification=True, parse_mode='html')


@dp.message_handler(lambda message: UsersDbManager.sync_get_context(message.chat.id).startswith('wait_agent_id-'),
                    content_types=['text'])
async def seller_registration_wait_patronymic(message):
    tel_id = message.chat.id
    phone_number = await UsersDbManager.get_context(tel_id, loop)
    phone_number = phone_number.split('-')[-1]
    agent_descr = await RDB.get_agent_description(message.text, loop)
    if len(agent_descr) > 0:
        await UsersDbManager.create_user(phone_number, message.text, loop)
        await UsersDbManager.update_descr_by_phone(phone_number, re.sub(' +', ' ', str(agent_descr[0][1]).strip()),
                                                   loop)
        await UsersDbManager.update_context(tel_id, '0', loop)
        text = f"Агент <b><u>{re.sub(' +', ' ', str(agent_descr[0][1]).strip())}({message.text})</u></b> " \
               f"с номером телефона <b><u>{phone_number}</u></b> добавлен!"
        await bot.send_message(tel_id, text, reply_markup=mk.admin_menu,
                               disable_notification=True, parse_mode='html')
    else:
        await UsersDbManager.update_context(tel_id, '0', loop)
        text = f'❌ Агента с ID <b>{message.text}</b> не существует в БД SOUZ! ❌'
        await bot.send_message(tel_id, text, reply_markup=mk.admin_menu,
                               disable_notification=True, parse_mode='html')


@dp.message_handler(lambda message: message.text == '⛔️ Исключить агента')
async def reff_link(message):
    tel_id = message.chat.id
    text = 'Выберите агента:'
    users = await UsersDbManager.get_all_active(loop)
    keyb = InlineKeyboardMarkup()
    for user in users:
        keyb.add(
            InlineKeyboardButton(f"{user.descr}({user.id_in_db}) {user.phone}",
                                 callback_data=f"kick*{user.id_in_db}"))
    await bot.send_message(tel_id, text, reply_markup=keyb,
                           disable_notification=True, parse_mode='html')


@dp.callback_query_handler(lambda call: call.data.startswith('kick*'))
async def choose_language(call: types.CallbackQuery):
    tel_id = call.from_user.id
    agent_id = call.data.split('*')[-1]
    agent = await UsersDbManager.get_user_by_agent_id(agent_id, loop)
    text = f'''Вы подтверждаете исключение агента:
<b>{agent.descr} ({agent.id_in_db}) - {agent.phone}</b> ?
'''
    keyb = InlineKeyboardMarkup()
    keyb.row(
        InlineKeyboardButton(f"❌ Нет",
                             callback_data=f"notconfirmKick*{agent_id}"),
        InlineKeyboardButton(f"✅ Да",
                             callback_data=f"confirmKick*{agent_id}")
    )
    await bot.edit_message_text(text, tel_id, call.message.message_id, reply_markup=keyb, parse_mode='html')


@dp.callback_query_handler(lambda call: call.data.startswith('confirmKick*'))
async def choose_language(call: types.CallbackQuery):
    tel_id = call.from_user.id
    agent_id = call.data.split('*')[-1]
    agent = await UsersDbManager.get_user_by_agent_id(agent_id, loop)
    await UsersDbManager.block_user_by_id(agent_id, loop)
    text = f'''✅ Агент <b>{agent.descr} ({agent.id_in_db}) - {agent.phone}</b> исключен!'''
    await bot.delete_message(tel_id, message_id=call.message.message_id)
    await bot.send_message(tel_id, text, reply_markup=mk.admin_menu, disable_notification=True, parse_mode='html')



@dp.callback_query_handler(lambda call: call.data.startswith('notconfirmKick*'))
async def choose_language(call: types.CallbackQuery):
    tel_id = call.from_user.id
    text = f'''❌ Действие отменено!'''
    await bot.delete_message(tel_id, message_id=call.message.message_id)
    await bot.send_message(tel_id, text, reply_markup=mk.admin_menu, disable_notification=True, parse_mode='html')


@dp.message_handler(lambda message: UsersDbManager.sync_get_context(message.chat.id) == 'kick_wait_phone_number',
                    content_types=['text'])
async def seller_registration_wait_patronymic(message):
    tel_id = message.chat.id
    if not PHONE_MASK.match(message.text):
        await bot.send_message(tel_id, msg.not_correct_phone_format, disable_notification=True, parse_mode='html')
        return
    if await UsersDbManager.get_user_by_phone(message.text, loop) is None:
        text = 'Агента с таким номером телефона не существует в базе чат-бота!'
        await bot.send_message(tel_id, text, reply_markup=mk.admin_menu,
                               disable_notification=True, parse_mode='html')
        await UsersDbManager.update_context(tel_id, f'0', loop)
        return
    text = f'Агент исключен!'
    await UsersDbManager.block_user(message.text, loop)
    await bot.send_message(tel_id, text, reply_markup=mk.admin_menu,
                           disable_notification=True, parse_mode='html')
    await UsersDbManager.update_context(tel_id, f'0', loop)


@dp.message_handler(lambda message: message.text == '⛔️ Исключить по ID агента')
async def reff_link(message):
    tel_id = message.chat.id
    # if tel_id not in ADMINS:
    #     await bot.send_message(tel_id, msg.no_admin_text,
    #                            disable_notification=True, parse_mode='html')
    #     return
    text = 'Введите ID агента'
    await bot.send_message(tel_id, text, reply_markup=mk.cancel,
                           disable_notification=True, parse_mode='html')
    await UsersDbManager.update_context(tel_id, 'kick_wait_agent_id', loop)


@dp.message_handler(lambda message: UsersDbManager.sync_get_context(message.chat.id) == 'kick_wait_agent_id',
                    content_types=['text'])
async def seller_registration_wait_patronymic(message):
    tel_id = message.chat.id
    if await UsersDbManager.get_user_by_agent_id(message.text, loop) is None:
        text = 'Агента с таким ID не существует в базе чат-бота!'
        await bot.send_message(tel_id, text, reply_markup=mk.admin_menu,
                               disable_notification=True, parse_mode='html')
        await UsersDbManager.update_context(tel_id, f'0', loop)
        return
    text = f'Агент исключен!'
    await UsersDbManager.block_user_by_id(message.text, loop)
    await bot.send_message(tel_id, text, reply_markup=mk.admin_menu,
                           disable_notification=True, parse_mode='html')
    await UsersDbManager.update_context(tel_id, f'0', loop)


def normalize_phone_number(phone_number):
    phone_number = ''.join(filter(str.isdigit, phone_number))

    if phone_number.startswith('8'):
        phone_number = '3' + phone_number

    if phone_number.startswith('0'):
        phone_number = '38' + phone_number[1:]

    if phone_number.startswith('+'):
        phone_number = phone_number[1:]

    if not phone_number.startswith('380'):
        phone_number = '380' + phone_number

    if len(phone_number) != 12:
        return None

    return phone_number


def normalize_phone_number_plus(phone_number):
    cleaned_number = re.sub(r'\D', '', phone_number)

    if len(cleaned_number) == 10 and cleaned_number.startswith('0'):
        normalized_number = '+380' + cleaned_number[1:]
    elif len(cleaned_number) == 12 and cleaned_number.startswith('380'):
        normalized_number = '+380' + cleaned_number[3:]
    elif len(cleaned_number) == 13 and cleaned_number.startswith('+380'):
        normalized_number = cleaned_number
    else:
        return ''
    return normalized_number


@dp.message_handler(lambda message: message.text == '🚛 Все экспедиторы')
async def reff_link(message):
    tel_id = message.chat.id
    text = 'Поиск ...'
    mess = await bot.send_message(tel_id, text,
                                  disable_notification=True, parse_mode='html')
    clients = await RDB.get_expeditors(loop)
    await bot.delete_message(tel_id, mess.message_id)
    if len(clients) > 0:
        sorted_clients = []
        for client in clients:
            if not any(sublist[0] == client[0] for sublist in sorted_clients):
                sorted_clients.append([client[0], client[1], [client]])
            else:
                for c in sorted_clients:
                    if c[0] == client[0]:
                        c[2].append(client)
                        break
        keyb = InlineKeyboardMarkup()
        for client in sorted_clients:
            keyb.add(
                InlineKeyboardButton(client[1], callback_data=f"plusemi*{re.sub(' +', ' ', str(client[0]).strip())}"))
        await bot.send_message(tel_id, msg.clients_list, reply_markup=keyb, parse_mode='html',
                               disable_notification=True)
    else:
        await bot.send_message(tel_id, msg.no_clients_today,
                               reply_markup=mk.main_menu(tel_id in ADMINS), parse_mode='html',
                               disable_notification=True)


def split_message(text):
    messages = []
    while len(text) > 4096:
        split_pos = text.rfind('\n', 0, 4096)
        if split_pos == -1:
            split_pos = 4096
        messages.append(text[:split_pos])
        text = text[split_pos:]
    messages.append(text)
    return messages


@dp.callback_query_handler(lambda call: call.data.startswith('plusemi*'))
async def choose_language(call: types.CallbackQuery):
    tel_id = call.from_user.id
    user = await UsersDbManager.get_user(tel_id, loop)
    if user.is_blocked:
        text = msg.user_not_exists
        await bot.send_message(tel_id, text,
                               disable_notification=True, parse_mode='html')
        return
    expeditor_id = call.data.split('*')[-1]
    text = 'Поиск ...'
    mess = await bot.send_message(tel_id, text,
                                  disable_notification=True, parse_mode='html')
    clients = await RDB.get_expeditor_clients(expeditor_id, loop)
    await bot.delete_message(tel_id, mess.message_id)
    # print(str(clients[0][7]), normalize_phone_number_plus(str(clients[0][7])))
    text = msg.expeditor_header_with_phone.format(
        f"{re.sub(' +', ' ', str(clients[0][0]).strip())}", normalize_phone_number_plus(str(clients[0][7])))
    routes = []
    points = []
    for client in clients:
        if client[3] not in routes:
            if routes != []:
                text += '\n ---------- \n '
            # last_checkin = await RDB.get_expeditor_last_checkin(expeditor_id, client[3], loop)
            last_checkin = find_last_checkin(clients, client[3])
            text += f'\n {msg.route_header_html.format(client[3])} \n '
            text += f'''\n {msg.last_checkin.format(f"точка {last_checkin[0]} в {last_checkin[1].split()[1][:5] if last_checkin[1] != 'None' else '-----'}"
                                                    if last_checkin != -1 else '-----')} \n '''
            if is_all_points(clients, client[3]):
                text += f'\n {msg.all_points_complete} \n '
            routes.append(client[3])
        client_name = re.sub(' +', ' ', str(client[2]).strip())
        # client_id = re.sub(' +', ' ', str(client[3]).strip())
        if client[4] not in points:
            points.append(client[4])
            if client[5] is not None:
                if client[6] == 'S' or client[6] is None:
                    text += '\n' + msg.expeditor_client_shipped_text.format(client_name, client[4],
                                                                            str(client[5]).split()[1][:5]) + '\n '
                elif client[6] == 'SA':
                    text += '\n' + msg.expeditor_client_shipped_with_adjustment_text.format(client_name, client[4],
                                                                                            str(client[5]).split()[1][
                                                                                            :5]) + '\n '
                else:
                    text += '\n' + msg.expeditor_client_refused_text.format(client_name, client[4],
                                                                            str(client[5]).split()[1][:5]) + '\n '
            else:
                text += '\n' + msg.expeditor_client_on_way_text.format(client_name, client[4]) + '\n '
    keyb = InlineKeyboardMarkup()
    keyb.add(
        InlineKeyboardButton("⬅️ Список экспедиторов", callback_data=f"plusexpeditors_back"))
    res_text = split_message(text)
    if len(res_text) == 1:
        await bot.edit_message_text(res_text[0], tel_id, call.message.message_id, parse_mode='html', reply_markup=keyb)
    else:
        for t in res_text:
            if t != res_text[len(res_text) - 1]:
                await bot.send_message(tel_id, t, parse_mode='html')
            else:
                await bot.send_message(tel_id, t, parse_mode='html', reply_markup=keyb)


def find_last_checkin(clients, route):
    lc = -1
    for client in clients:
        if client[3] == route:
            if lc == -1:
                if client[5] is not None:
                    lc = [client[4], str(client[5])]
            else:
                if int(client[4]) > lc[0] and client[5] is not None:
                    lc = [client[4], str(client[5])]
    return lc


def is_all_points(clients, route):
    max_point = 0
    on_way_points_count = 0
    for client in clients:
        if client[3] == route and client[5] is not None:
            on_way_points_count += 1
            max_point = client[4]
    return (on_way_points_count >= max_point) and on_way_points_count != 0 and max_point != 0


@dp.callback_query_handler(lambda call: call.data.startswith('plusexpeditors_back'))
async def choose_language(call: types.CallbackQuery):
    tel_id = call.from_user.id
    clients = await RDB.get_expeditors(loop)
    if len(clients) > 0:
        sorted_clients = []
        for client in clients:
            if not any(sublist[0] == client[0] for sublist in sorted_clients):
                sorted_clients.append([client[0], client[1], [client]])
            else:
                for c in sorted_clients:
                    if c[0] == client[0]:
                        c[2].append(client)
                        break
        keyb = InlineKeyboardMarkup()
        for client in sorted_clients:
            keyb.add(
                InlineKeyboardButton(client[1], callback_data=f"plusemi*{re.sub(' +', ' ', str(client[0]).strip())}"))
        await bot.send_message(tel_id, msg.clients_list, reply_markup=keyb, parse_mode='html',
                               disable_notification=True)
    else:
        await bot.send_message(tel_id, msg.no_clients_today,
                               reply_markup=mk.main_menu(tel_id in ADMINS), parse_mode='html',
                               disable_notification=True)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
