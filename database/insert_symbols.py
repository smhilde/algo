import sqlalchemy as sql
import datetime
import requests
import toolz
from bs4 import BeautifulSoup

def get_table_rows(table):
    return table.select('tr')[1:] # Assume that the table has a header

def get_tables(response):
    return BeautifulSoup(response.text, 'lxml').select('table')

def get_symbol_html_rows(url):
    return toolz.compose(get_table_rows,
                         toolz.first,
                         get_tables,
                         requests.get)(url)

def row_to_entry(row):
    now = datetime.datetime.utcnow()
    columns = row.select('td')
    return {'ticker': columns[0].text,
            'instrument': 'stock',
            'name': columns[1].text,
            'sector': columns[3].text,
            'currency': 'USD',
            'created_date': now,
            'last_updated_date': now}

def create_symbol_db_entries(symbol_rows):
    return map(row_to_entry, symbol_rows)

def get_entries(url):
    return list(toolz.compose(create_symbol_db_entries,
                              get_symbol_html_rows)(url))

def insert_symbols(state):
    results_prx = state['conn'].execute(sql.insert(state['table']), state['values'])
    return toolz.assoc(state, 'inserted_rows', results_prx.rowcount)


if __name__ == '__main__':
    engine = sql.create_engine('mysql+mysqldb://quant:na442h16@localhost/securities_master')
    conn = engine.connect()
    meta = sql.MetaData()
    symbols = sql.Table('symbol', meta, autoload=True, autoload_with=engine)

    insert_symbols({'conn': conn,
                    'table': symbols,
                    'values': get_entries(r'http://en.wikipedia.org/wiki/List_of_S%26P_500_companies')})

    conn.close()
