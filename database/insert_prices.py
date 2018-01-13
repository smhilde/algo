#!/home/quant/anaconda3/bin/python
# -*- coding: utf-8 -*-

# insert_prices.py

import datetime
import warnings
import toolz
import requests
import sqlalchemy as sql
import quandl
from vendor import get_id_url
from utilities import reflect_table, create_engine, insert

quandl.ApiConfig.api_key = 'd_vCyt5y-zi-zTBbWsK_'

def get_symbols(engine, table):
    with engine.connect() as conn:
        stmt = sql.select([table.c.id, table.c.ticker])
        return conn.execute(stmt).fetchall()

"""
def yahoo_qrystr(symbol, start, end):
    return dict(ticker=symbol,
                start_month=start.month-1,
                start_day=start.day,
                start_year=start.year, 
                end_month=end.month-1,
                end_day=end.day,
                end_year=end.year)

def price_dict(symbol_id, price):
    return dict(price_date=datetime.datetime.strptime(price[0], '%Y-%m-%d'), 
                open_price=price[1],
                high_price=price[2],
                low_price=price[3],
                close_price=price[4],
                adj_close_price=price[5],
                volume=price[6],
                symbol_id=symbol_id)


# this only works with yahoo
@toolz.curry
def get_yahoo_daily_prices(url, start_date, end_date, symbol):
    try:
        yf_data = requests.get(url.format(**yahoo_qrystr(symbol[1], start_date, end_date))).text.split('\n')[1:-1]
        prices = [price_dict(symbol[0], y.strip().split(',')) for y in yf_data]
        print('\t> Fetched {} prices for {}.'.format(len(prices), symbol[1]))
    except Exception as e:
        print('Could not download Yahoo data: %s' % e)
        return []
    return prices

@toolz.curry
def entry_maker(vendor_id, daily_price):
    # create the time now
    now = datetime.datetime.utcnow()
    return {**daily_price, **{'data_vendor_id': vendor_id,
                              'created_date': now,
                              'last_updated_date': now}}
"""

# for quandl
@toolz.curry
def get_daily_prices(vendor, start_date, end_date, symbol):
    print('\t> Retrieving data for {}.'.format(symbol[1]))
    quandl_data = quandl.get_table('WIKI/PRICES',
                                   ticker=symbol[1],
                                   date=dict(gte=start_date, lte=end_date),
                                   qopts=dict(columns=['date', 'open', 'high', 'low', 
                                                       'close', 'adj_close', 'adj_volume']))
    if quandl_data.shape[0] == 0: # returned an empty data frame
        return
    return quandl_data.assign(data_vendor_id=vendor[0],
                              created_date=datetime.datetime.utcnow(),
                              last_updated_date=datetime.datetime.utcnow(),
                              symbol_id=symbol[0]).\
                       rename(columns=dict(date='price_date',
                                           open='open_price',
                                           high='high_price',
                                           low='low_price',
                                           close='close_price',
                                           adj_close='adj_close_price',
                                           adj_volume='volume')).\
                       to_dict(orient='records')

@toolz.curry
def insert_prices(engine, price_table, daily_prices):
    """
    Takes a list of dictionaries of daily price data and adds it to the MySQL
    database. Appends the vendor ID and symbol ID to the data before
    inserting into database.
    
    state:        Dictionary containing the engine, the price table,
                  the vendor id, and a list of symbol tuples. The first entry
                  of the tuple is the symbol id, the second the ticker.
    daily_prices: List of dictionaries of the OHLC data
                  (with adjusted close and volume)
    """
    if not daily_prices:
        return
    if len(daily_prices) > 1000:
        insert(engine, price_table, daily_prices[:1000])
        insert_prices(engine, price_table, daily_prices[1001:])
    else:
        insert(engine, price_table, daily_prices)

def process_symbols(state):
    process = toolz.compose(insert_prices(state['engine'],
                                          state['price_table']),
                            get_daily_prices(state['vendor'],
                                             state['start_date'],
                                             state['end_date']))
    for symbol in state['symbols']:
        process(symbol)

if __name__ == '__main__':
    # This ignores the warnings regarding Data Truncation to Decimal(19,4) datatypes
    warnings.filterwarnings('ignore')

    engine = create_engine()
    symbol = reflect_table(engine, 'symbol')

    """
    # needed when building for the first time. typically we'll process all symbols.
    # ------------
    # I need all of this to select the symbols to process.
    price = reflect_table(engine, 'daily_price')
    stmt = (sql.select([symbol.c.id, symbol.c.ticker])
               .select_from(symbol.join(price, symbol.c.id==price.c.symbol_id, isouter=True))
               .where(price.c.symbol_id==None))
    with engine.connect() as conn: 
        symbols_to_process = conn.execute(stmt).fetchall()
    # ------------
    """
    symbols_to_process = get_symbols(engine, symbol)
    print('Processing {} symbols'.format(len(symbols_to_process)))
    #v_id, url = get_id_url(engine, 'yahoo')
    process_symbols({'engine': engine,
                     'symbols': symbols_to_process,
                     'vendor': get_id_url(engine, 'quandl'),
                     'start_date': datetime.date(2000, 1, 3),
                     'end_date': datetime.date.today(), # 11 JUN 2017
                     'price_table': reflect_table(engine, 'daily_price')})
