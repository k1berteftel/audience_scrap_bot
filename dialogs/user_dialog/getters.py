import os
import random

from aiogram import Bot
from aiogram.types import CallbackQuery, User, Message, ContentType
from aiogram_dialog import DialogManager, ShowMode
from aiogram_dialog.api.entities import MediaAttachment
from aiogram_dialog.widgets.kbd import Button, Select
from aiogram_dialog.widgets.input import ManagedTextInput, MessageInput
from pyrogram import Client
from pyrogram.types import SentCode
from pyrogram.errors import PasswordHashInvalid
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from utils.account_functions import get_channels
from utils.collect_funcs import collect_users_base
from utils.tables import get_table
from utils.schedulers import send_message
from database.db_conf import database
from config_data.config import load_config, Config
from states.state_groups import startSG


db = database('accounts.sqlite3')


config: Config = load_config()

api_id = config.user_bot.api_id
api_hash = config.user_bot.api_hash

proxy_data = config.proxy

proxy = {
    'scheme': proxy_data.scheme,
    'hostname': proxy_data.hostname,
    'port': proxy_data.port,
    'username': proxy_data.username,
    'password': proxy_data.password
}


async def start_malling(clb: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    users = dialog_manager.dialog_data.get('users')
    text = dialog_manager.dialog_data.get('text')
    scheduler: AsyncIOScheduler = dialog_manager.middleware_data.get('scheduler')
    bot: Bot = dialog_manager.middleware_data.get('bot')
    await clb.message.answer('Началась рассылка сообщения, по завершению рассылки вы получите уведомление')
    scheduler.add_job(
        send_message,
        'interval',
        args=[clb.from_user.id, bot, users, text, scheduler],
        kwargs={'count': dialog_manager.dialog_data.get('count')},
        id=f'{clb.from_user.id}_malling',
        seconds=5
    )
    users = users[:dialog_manager.dialog_data.get('count'):]
    dialog_manager.dialog_data['users'] = users
    await dialog_manager.switch_to(startSG.base_menu, show_mode=ShowMode.DELETE_AND_SEND)


async def confirm_malling_getter(event_from_user: User, dialog_manager: DialogManager, **kwargs):
    count = dialog_manager.dialog_data.get('count')
    users = dialog_manager.dialog_data.get('users')[:count:]
    app = Client(str(event_from_user.id), api_id, api_hash)  # proxy=proxy
    await app.connect()
    account = await app.get_me()
    name = account.first_name if account.first_name else account.last_name if account.last_name else '-'
    await app.disconnect()
    return {
        'users': len(users),
        'account': name
    }


async def get_text(msg: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str):
    dialog_manager.dialog_data['text'] = msg.html_text
    await dialog_manager.switch_to(startSG.get_user_count)


async def get_user_count(msg: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str):
    try:
        count = int(text)
    except Exception:
        await msg.answer('Кол-во людей должно быть числом, пожалуйста попробуйте снова')
        return
    dialog_manager.dialog_data['count'] = count
    await dialog_manager.switch_to(startSG.confirm_malling)


async def base_menu_getter(event_from_user: User, dialog_manager: DialogManager, **kwargs):
    users = dialog_manager.dialog_data.get('users')
    if users is None:
        users = []
        dialog_manager.dialog_data['users'] = users
    media = None
    if users:
        table = get_table(users, f'{event_from_user.id}_base')
        media = MediaAttachment(type=ContentType.DOCUMENT, path=table)
    return {
        'users': len(users),
        'document': media if media else False
    }


async def clean_base(clb: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    users = dialog_manager.dialog_data.get('users')
    dialog_manager.dialog_data['users'] = None
    await clb.answer('База пользователей была успешно почищена')
    await dialog_manager.switch_to(startSG.base_menu)


async def check_base(clb: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    account = db.get_account(clb.from_user.id)
    if not account:
        await clb.answer('Чтобы пользоваться данными функциями пожалуйста подключите аккаунт')
        await dialog_manager.switch_to(startSG.accounts)
        return
    users = dialog_manager.dialog_data.get('users')
    if not users:
        await clb.answer('Ваша база пользователей пустая, чтобы продолжить соберите базу')
        return
    await dialog_manager.switch_to(startSG.get_mail)


async def get_channel(msg: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str):
    try:
        text = int(text)
    except Exception as err:
        print(err)
        if 't.me' not in text:
            await msg.answer('Вы ввели ссылку не в том формате, пожалуйста попробуйте снова')
            return
        try:
            text = text.split('/')[-1]
        except Exception:
            await msg.answer('Вы ввели ссылку не в том формате, пожалуйста попробуйте снова')
            return

    if not db.get_account(msg.from_user.id):
        await msg.answer('Чтобы собрать базу с чата пожалуйста подключите аккаунт')
        await dialog_manager.switch_to(startSG.accounts)
        return
    message = await msg.answer('Начался процесс сбора базы')
    users = dialog_manager.dialog_data.get('users')
    users = await collect_users_base(msg.from_user.id, text, msg.bot, users)
    if not users:
        await msg.answer('При сборе базы произошла какая-то ошибка пожалуйста попробуйте снова')
        await dialog_manager.switch_to(startSG.base_menu)
        return
    random.shuffle(users)
    dialog_manager.dialog_data['users'] = users
    await message.delete()
    await dialog_manager.switch_to(startSG.base_menu)


async def my_channels_getter(event_from_user: User, dialog_manager: DialogManager, **kwargs):
    page = dialog_manager.dialog_data.get('chat_page')
    account = db.get_account(event_from_user.id)
    bot: Bot = dialog_manager.middleware_data.get('bot')
    if not account:
        await bot.send_message(
            chat_id=event_from_user.id,
            text='У вас не привязано аккаунтов для парсинга'
        )
        await dialog_manager.switch_to(startSG.accounts)
        return
    bot: Bot = dialog_manager.middleware_data.get('bot')
    if not page:
        page = 0
        dialog_manager.dialog_data['chat_page'] = page
    dialogs = dialog_manager.dialog_data.get('chats')
    if not dialogs:
        dialogs = await get_channels(account, bot, event_from_user.id)
        dialogs = [dialogs[i:i + 20] for i in range(0, len(dialogs), 20)]
        dialog_manager.dialog_data['chats'] = dialogs
    not_first = True
    not_last = True
    if page == 0:
        not_first = False
    if page == len(dialogs) - 1:
        not_last = False
    return {
        'items': dialogs[page],
        'not_first': not_first,
        'not_last': not_last,
        'open_page': str(page + 1),
        'last_page': str(len(dialogs))
    }


async def my_channels_pager(clb: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    page = dialog_manager.dialog_data.get('chat_page')
    if clb.data.startswith('back'):
        dialog_manager.dialog_data['chat_page'] = page - 1
    else:
        dialog_manager.dialog_data['chat_page'] = page + 1
    await dialog_manager.switch_to(startSG.my_channels)


async def my_chat_selector(clb: CallbackQuery, widget: Select, dialog_manager: DialogManager, item_id: str):
    await clb.answer('Начался процесс считывания базы пользователей')
    users = dialog_manager.dialog_data.get('users')
    users = await collect_users_base(clb.from_user.id, int(item_id), clb.bot, users)
    if not users:
        await clb.message.answer('При сборе базы произошла какая-то ошибка пожалуйста попробуйте снова')
        await dialog_manager.switch_to(startSG.base_menu)
        return
    random.shuffle(users)
    dialog_manager.dialog_data['users'] = users
    await dialog_manager.switch_to(startSG.base_menu)


async def get_forward_message(msg: Message, widget: MessageInput, dialog_manager: DialogManager):
    if msg.forward_from_chat is None:
        await msg.answer('К сожалению невозможно получить данные о канале из-за правил конфеденциальности канала')
        return
    if not db.get_account(msg.from_user.id):
        await msg.answer('Чтобы собрать базу с чата пожалуйста подключите свой аккаунт')
        await dialog_manager.switch_to(startSG.accounts)
        return
    bot: Bot = dialog_manager.middleware_data.get('bot')
    users = dialog_manager.dialog_data.get('users')
    users = await collect_users_base(msg.from_user.id, msg.forward_from_chat.id, msg.bot, users)
    if not users:
        await msg.answer('При сборе базы произошла какая-то ошибка пожалуйста попробуйте снова')
        await dialog_manager.switch_to(startSG.base_menu)
        return
    random.shuffle(users)
    dialog_manager.dialog_data['users'] = users
    await dialog_manager.switch_to(startSG.base_menu)


async def del_account(clb: CallbackQuery, button: Button, dialog_manager: DialogManager):
    account = db.get_account(user_id=clb.from_user.id)
    db.del_account(clb.from_user.id)
    try:
        os.remove(account)
    except Exception as err:
        print(err)
    await dialog_manager.switch_to(state=startSG.accounts)


async def check_account_del(clb: CallbackQuery, button: Button, dialog_manager: DialogManager):
    if not db.get_account(clb.from_user.id):
        await clb.answer('У вас отсутствует аккаунт для удаления')
        return
    await dialog_manager.switch_to(state=startSG.del_account)


async def check_account(clb: CallbackQuery, button: Button, dialog_manager: DialogManager):
    if db.get_account(clb.from_user.id):
        await clb.answer('Вы уже имеете привязанный аккаунт')
        return
    await dialog_manager.switch_to(state=startSG.add_account)


async def phone_get(message: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str):
    print('Начало соединения')
    client = Client(f'{message.from_user.id}', api_id, api_hash)  # proxy=proxy
    await client.connect()
    print(text, type(text))
    try:
        print('Отправка кода')
        sent_code_info: SentCode = await client.send_code(text.strip())
    except Exception as err:
        print(err)
        await message.answer('Веденный номер телефона неверен, попробуйте снова')
        return
    dialog_manager.dialog_data['client'] = client
    dialog_manager.dialog_data['phone_info'] = sent_code_info
    dialog_manager.dialog_data['phone_number'] = text
    await dialog_manager.switch_to(state=startSG.kod_send)


async def get_kod(message: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str):
    client: Client = dialog_manager.dialog_data.get('client')
    phone_info: SentCode = dialog_manager.dialog_data.get('phone_info')
    phone = dialog_manager.dialog_data.get('phone_number')
    code = ''
    if len(text.split('-')) != 5:
        await message.answer(text='Вы отправили код в неправильном формате, попробуйте вести код снова')
        return
    for number in text.split('-'):
        code += number
    print(code)
    try:
        await client.sign_in(phone, phone_info.phone_code_hash, code)
        await client.disconnect()
        db.add_account(message.from_user.id, account=str(message.from_user.id))
        dialog_manager.dialog_data.clear()
        await dialog_manager.switch_to(state=startSG.accounts)
    except Exception as err:
        print(err)
        await dialog_manager.switch_to(state=startSG.password)


async def get_password(message: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str):
    client: Client = dialog_manager.dialog_data.get('client')
    phone_info = dialog_manager.dialog_data.get('phone_info')
    phone = dialog_manager.dialog_data.get('phone_number')

    try:
        await client.check_password(text)
        await client.disconnect()
        db.add_account(message.from_user.id, account=str(message.from_user.id))
        await message.answer(text='Ваш аккаунт был успешно добавлен')
        dialog_manager.dialog_data.clear()
        await dialog_manager.switch_to(state=startSG.accounts)
    except PasswordHashInvalid as err:
        print(err)
        await message.answer(text='Введенные данные были неверны, пожалуйста попробуйте авторизоваться снова')
        await dialog_manager.switch_to(state=startSG.add_account)

