from pyrogram import Client

from database.db_conf import database


proxy = {
    'scheme': 'http',
    'hostname': '109.205.62.47',
    'port': 64856,
    'username': 'eAzEJHXk',
    'password': '6WL4egih'
}


async def collect_users_base(account: str, channel: str | int, users: list[list] | None = None) -> list[list] | bool:
    if users is None:
        users = []
    try:
        app = Client(account, proxy=proxy)
    except Exception as err:
        print(err)
        return False
    async with app:
        new_users = []
        ids = [user[0] for user in users]
        members = app.get_chat_members(channel)
        try:
            async for user in members:
                if user.user.username and not user.user.is_bot and not user.user.is_contact and not user.user.is_fake:
                    if user.user.id not in ids:
                        new_users.append(
                            [
                                user.user.id,
                                '@' + user.user.username,
                                user.user.first_name if user.user.first_name else '-',
                                user.user.phone_number if user.user.phone_number else '-'
                            ]
                        )
            if len(new_users) > 30:
                users.extend(new_users)
            else:
                user_ids = []
                async for message in app.get_chat_history(channel, limit=1500):
                    user = message.from_user
                    if user and (not user.is_bot and not user.is_fake) and user.id not in [usr[0] for usr in user_ids] and user.username:
                        user_ids.append(
                            [
                                user.id,
                                '@' + user.username,
                                user.first_name if user.first_name else '-',
                                user.phone_number if user.phone_number else '-'
                            ]
                        )
                users.extend(user_ids)
        except Exception as err:
            print(err, err.args, err.__traceback__)

    n = len(users)
    for i in range(n):
        for j in range(0, n-i-1):
            if isinstance(users[j+1][3], int) and not isinstance(users[j][3], int):
                users[j], users[j + 1] = users[j + 1], users[j]
    return users if users else False

