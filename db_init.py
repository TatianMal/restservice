from envparse import Env
from sqlalchemy import create_engine, MetaData
from db import limits, payments
from datetime import datetime
env = Env(
    USER=str,
    PASSWORD=str,
    HOST=str,
    PORT=int,
    DATABASE=str
)
env.read_envfile()

DSN = "postgresql://{user}:{password}@{host}:{port}/{database}"


def init_default_values(engine):
    conn = engine.connect()
    conn.execute(limits.insert(), [
        {'country': "AUS", 'currency': "USD", 'max_per_month': 100000},
        {'country': "RUS", 'currency': "RUB", 'max_per_month': 3500000},
        {'country': "AUS", 'currency': "EUR", 'max_per_month': 75000},
        {'country': "ABH", 'currency': "RUB", 'max_per_month': 2000000},
        {'country': "RUS", 'currency': "USD", 'max_per_month': 400000}
    ])
    conn.execute(payments.insert(), [
        {'id_client': 4511, 'date_transfer': datetime(2019, 4, 7, 20, 8, 3),
         'transfer_amount': 45000, 'country': "ABH", 'currency': "RUB"},
        {'id_client': 4328, 'date_transfer': datetime(2019, 4, 14, 10, 2, 41),
         'transfer_amount': 7800, 'country': "RUS", 'currency': "USD"},
        {'id_client': 4511, 'date_transfer': datetime(2019, 5, 14, 10, 2, 41),
         'transfer_amount': 50000, 'country': "AUS", 'currency': "USD"},
        {'id_client': 4240, 'date_transfer': datetime(2019, 5, 20, 17, 24, 0),
         'transfer_amount': 5150, 'country': "AUS", 'currency': "EUR"},
        {'id_client': 4511, 'date_transfer': datetime(2019, 5, 26, 7, 20, 00),
         'transfer_amount': 40000, 'country': "AUS", 'currency': "USD"}
    ])
    conn.close()


if __name__ == '__main__':
    args = {
        'user': env.str('USER'),
        'password': env.str('PASSWORD'),
        'host': env.str('HOST'),
        'port': env.int('PORT'),
        'database': env.str('DATABASE')
    }
    db_url = DSN.format(**args)
    meta = MetaData()
    engine = create_engine(db_url)

    meta.drop_all(bind=engine, tables=[limits, payments])
    meta.create_all(bind=engine, tables=[limits, payments])
    init_default_values(engine)

