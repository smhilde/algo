import pandas as pd
import sqlalchemy as sql
from utilities import reflect_table, create_engine

def get_price(ticker, start_date, end_date):
    engine = create_engine()
    symbol = reflect_table(engine, 'symbol')
    price = reflect_table(engine, 'daily_price')

    stmt = sql.select([price]).select_from(price.\
               join(symbol, price.c.symbol_id == symbol.c.id)).\
               where(sql.and_(symbol.c.ticker==ticker,
                              price.c.date.between(start_date, end_date)))

    with engine.connect() as conn:
        return pd.DataFrame(conn.execute(stmt).fetchall())
