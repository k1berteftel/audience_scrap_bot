from aiogram.types import ContentType
from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import SwitchTo, Column, Row, Button, Group, Select, Start, Url
from aiogram_dialog.widgets.text import Format, Const
from aiogram_dialog.widgets.input import TextInput, MessageInput
from aiogram_dialog.widgets.media import DynamicMedia

from dialogs.user_dialog import getters

from states.state_groups import startSG

user_dialog = Dialog(
    Window(
        Const('Приветственный текст'),
        Column(
            SwitchTo(Const('Работа с базой пользователей'), id='base_menu_switcher', state=startSG.base_menu),
            SwitchTo(Const('Управление аккаунтами'), id='accounts_switcher', state=startSG.accounts),
        ),
        state=startSG.start
    ),
    Window(
        DynamicMedia('document', when='document'),
        Format('Пользователей в базе: {users}'),
        Column(
            SwitchTo(Const('Добавить пользователей в базу'), id='get_channel_switcher', state=startSG.get_channel),
            Button(Const('Сделать рассылку по базе пользователей'), id='malling_database_switcher', on_click=getters.check_base),
            Button(Const('Почистить базу'), id='clean_users_base', on_click=getters.clean_base),
        ),
        SwitchTo(Const('Назад'), id='back', state=startSG.start),
        getter=getters.base_menu_getter,
        state=startSG.base_menu
    ),
    Window(
        Const('Отправьте кол-во людей которым надо будет разослать данное сообщение'),
        TextInput(
            id='get_user_count',
            on_success=getters.get_user_count
        ),
        SwitchTo(Const('Отмена'), id='back_base_menu', state=startSG.base_menu),
        state=startSG.get_user_count
    ),
    Window(
        Const('Отправьте текстовое сообщение, которое надо будет разослать по базе пользователей'),
        TextInput(
            id='get_text',
            on_success=getters.get_text,
        ),
        SwitchTo(Const('Отмена'), id='back_base_menu', state=startSG.base_menu),
        state=startSG.get_mail
    ),
    Window(
        Format('Данное сообщение будет отправлено {users} с аккаунта {account}'
               '\n<b>Вы подтверждаете рассылку сообщения?</b>'),
        Row(
            Button(Const('Да'), id='start_malling', on_click=getters.start_malling),
            SwitchTo(Const('Нет'), id='back_base_menu', state=startSG.base_menu)
        ),
        SwitchTo(Const('Назад'), id='back_get_mail', state=startSG.get_mail),
        getter=getters.confirm_malling_getter,
        state=startSG.confirm_malling
    ),
    Window(
        Const('Введите ссылку на канал с которого надо будет собрать базу пользователей'
              '\n<em>Если же канал является закрытым, то перешлите любое сообщение из данного канала, чтобы'
              ' бот смог вручную достать необходимые данные</em>'),
        TextInput(
            id='get_channel_link',
            on_success=getters.get_channel
        ),
        MessageInput(
            func=getters.get_forward_message,
            content_types=ContentType.ANY
        ),
        SwitchTo(Const('Мои каналы|чаты'), id='my_channels_switcher', state=startSG.my_channels),
        SwitchTo(Const('Отмена'), id='back_base_menu', state=startSG.base_menu),
        state=startSG.get_channel
    ),
    Window(
        Const('Выберите канал | чат'),
        Group(
            Select(
                Format('{item[0]}'),
                id='my_chats_builder',
                item_id_getter=lambda x: x[1],
                items='items',
                on_click=getters.my_chat_selector
            ),
            width=1
        ),
        Row(
            Button(Const('◀️'), id='back_my_chat_pager', on_click=getters.my_channels_pager, when='not_first'),
            Button(Format('{open_page}/{last_page}'), id='pager'),
            Button(Const('▶️'), id='next_my_chat_pager', on_click=getters.my_channels_pager, when='not_last'),
        ),
        SwitchTo(Const('🔙Назад'), id='back_get_channel', state=startSG.get_channel),
        getter=getters.my_channels_getter,
        state=startSG.my_channels
    ),
    Window(
        Const('Меню привязки аккаунтов'),
        Column(
            Button(Const('Добавить аккаунт'), id='add_account', on_click=getters.check_account),
            Button(Const('Удалить аккаунт'), id='del_account', on_click=getters.check_account_del),
            SwitchTo(Const('Назад'), id='back', state=startSG.start)
        ),
        state=startSG.accounts
    ),
    Window(
        Const('Отправьте номер телефона'),
        SwitchTo(Const('Отмена'), id='back', state=startSG.start),
        TextInput(
            id='get_phone',
            on_success=getters.phone_get,
        ),
        state=startSG.add_account
    ),
    Window(
        Const('Удалить действующий привязанный аккаунт?'),
        Column(
            Button(Const('Да'), id='conf_del_account', on_click=getters.del_account),
            SwitchTo(Const('Назад'), id='back_to_accounts', state=startSG.accounts),
        ),
        state=startSG.del_account
    ),
    Window(
        Const('Введи код который пришел на твой аккаунт в телеграмм в формате: 1-2-3-5-6'),
        TextInput(
            id='get_kod',
            on_success=getters.get_kod,
        ),
        state=startSG.kod_send
    ),
    Window(
        Const('Пароль от аккаунта телеграмм'),
        TextInput(
            id='get_password',
            on_success=getters.get_password,
        ),
        state=startSG.password
    ),
)