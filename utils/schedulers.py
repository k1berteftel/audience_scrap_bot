import os
import asyncio

from aiogram import Bot
from aiogram.types import FSInputFile
from pyrogram import Client
from pyrogram.errors import FloodWait, PeerFlood
from pyrogram.enums import ParseMode
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from utils.tables import get_table
from utils.collect_funcs import collect_users_base


async def send_message(user_id: int, bot: Bot, users: list[list], text: str, scheduler: AsyncIOScheduler, **kwargs):
    job = scheduler.get_job(job_id=f'{user_id}_malling')
    if job:
        job.remove()
    count = kwargs.get('count')
    counter = 0
    try:
        app = Client(str(user_id))
    except Exception as err:
        print(err)
        return False
    async with app:
        for user in (users if not count else users[:count:]):
            try:
                await app.send_message(
                    chat_id=user[1],
                    text=text,
                    parse_mode=ParseMode.HTML
                )
                counter += 1
            except FloodWait:
                await asyncio.sleep(10)
            except PeerFlood:
                await asyncio.sleep(60)
                try:
                    await app.send_message(
                        chat_id=user[1],
                        text=text,
                        parse_mode=ParseMode.HTML
                    )
                except PeerFlood:
                    await asyncio.sleep(60 * 30)
            except Exception as err:
                print(err)
            await asyncio.sleep(30)
    await bot.send_message(
        chat_id=user_id,
        text=f'Рассылка сообщения прошла успешно, {counter} пользователей получили сообщение'
    )