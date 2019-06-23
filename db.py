from envparse import Env
from aiopg.sa import create_engine
from sqlalchemy import (
    MetaData, Table, Column, Integer, DateTime, Index
)
from sqlalchemy.dialects.postgresql import ENUM

env = Env(
    USER=str,
    PASSWORD=str,
    HOST=str,
    PORT=int,
    DATABASE=str
)
env.read_envfile()

meta = MetaData()
VALIDATED_CURRENCIES = ("RUB", "USD", "EUR")
VALIDATED_COUNTRIES = ("RUS", "ABH", "AUS")

countries = ENUM(*VALIDATED_COUNTRIES, name="countries", create_type=False)
currencies = ENUM(*VALIDATED_CURRENCIES, name="currencies", create_type=False)


limits = Table(
    'limits', meta,

    Column('id', Integer, primary_key=True),
    Column('country', countries, nullable=False),
    Column('currency', currencies, nullable=False),
    Column('max_per_month', Integer, nullable=False),
    Index("cur_count_index", "country", "currency")
)

payments = Table(
    'payments', meta,

    Column('id', Integer, primary_key=True),
    Column('id_client', Integer, nullable=False),
    Column('date_transfer', DateTime, nullable=False),
    Column('transfer_amount', Integer, nullable=False),
    Column('currency', currencies, nullable=False),
    Column('country', countries, nullable=False),
    Index("cur_count_index_payment", "country", "currency")
)


async def init_conn(app):
    args = {
        'user': env.str('USER'),
        'password': env.str('PASSWORD'),
        'host': env.str('HOST'),
        'port': env.int('PORT'),
        'database': env.str('DATABASE'),
        'minsize': env.int("MINSIZE"),
        'maxsize': env.int("MAXSIZE")
    }
    engine = await create_engine(**args)
    app['db'] = engine


async def close_conn(app):
    app['db'].close()
    await app['db'].wait_closed()
