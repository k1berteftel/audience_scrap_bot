import asyncio

from aiogram import Bot
from pyrogram import Client
from pyrogram.enums.chat_type import ChatType


api_id = 9238838
api_hash = 'b65e9edfabe1c645a0d101543f065e89'


async def get_channels(account: str, bot: Bot, user_id: int):
    try:
        app = Client(account)
    except Exception as err:
        print(err)
        await bot.send_message(
            chat_id=user_id,
            text='Срок привязанного аккаунта подошел к концу, пожалуйста удалите из бота существующий и привяжите его снова'
        )
        return
    dialogs = []
    async with app:
        async for dialog in app.get_dialogs():
            if dialog.chat.type not in [ChatType.BOT, ChatType.PRIVATE]:
                dialogs.append(
                    (
                        dialog.chat.title,
                        dialog.chat.id
                    )
                )
    return dialogs


async def get_chat(chat_id: int | str, account: str, bot: Bot, user_id: int):
    try:
        app = Client(account, api_id=api_id, api_hash=api_hash)
    except Exception as err:
        print(err.args)
        print(err)
        await bot.send_message(
            chat_id=user_id,
            text='Срок привязанного аккаунта подошел к концу, пожалуйста удалите из бота существующий и привяжите его снова'
        )
        return
    async with app:
        chat = await app.get_chat(chat_id)
    return chat
