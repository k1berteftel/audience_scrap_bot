from aiogram.fsm.state import State, StatesGroup

# Обычная группа состояний


class startSG(StatesGroup):
    start = State()
    base_menu = State()
    get_channel = State()
    my_channels = State()
    get_mail = State()
    get_user_count = State()
    confirm_malling = State()
    accounts = State()
    add_account = State()
    del_account = State()
    kod_send = State()
    password = State()

