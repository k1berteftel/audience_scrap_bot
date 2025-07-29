from dataclasses import dataclass

from environs import Env

'''
    При необходимости конфиг базы данных или других сторонних сервисов
'''


@dataclass
class tg_bot:
    token: str


@dataclass
class UserBot:
    api_id: int
    api_hash: str


@dataclass
class Proxy:
    scheme: str
    hostname: str
    port: int
    username: str
    password: str


@dataclass
class Config:
    bot: tg_bot
    user_bot: UserBot
    proxy: Proxy


def load_config(path: str | None = None) -> Config:
    env: Env = Env()
    env.read_env(path)

    return Config(
        bot=tg_bot(
            token=env('token')
            ),
        user_bot=UserBot(
            api_id=int(env('api_id')),
            api_hash=env('api_hash')
        ),
        proxy=Proxy(
            scheme=env('proxy_scheme'),
            hostname=env('proxy_hostname'),
            port=int(env('proxy_port')),
            username=env('proxy_username'),
            password=env('proxy_password')
        )
    )
