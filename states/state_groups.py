from aiogram.fsm.state import State, StatesGroup

# Обычная группа состояний


class startSG(StatesGroup):
    start = State()


class adminSG(StatesGroup):
    start = State()
    get_mail = State()
    get_time = State()
    get_keyboard = State()
    confirm_mail = State()
    deeplink_menu = State()
    deeplink_del = State()
    admin_menu = State()
    admin_del = State()
    admin_add = State()
