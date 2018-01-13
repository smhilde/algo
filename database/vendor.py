#!/usr/bin/python

import sqlalchemy as sql
import datetime
from utilities import reflect_table, insert, create_engine

def get_id_url(engine, vendor):
    v = reflect_table(engine, 'data_vendor')
    with engine.connect() as conn:
        return (conn.execute(sql.select([v.c.id, v.c.website_url])
                                .where(v.c.name == vendor.lower()))
                    .first())

def update_db(state):
    insert(state['engine'], state['vendor_table'], state['vendor_list'])


if __name__ == '__main__':
    engine = create_engine()
    now = datetime.datetime.utcnow()
    vendors = [dict(name='quandl',
                    website_url='https://www.quandl.com',
                    created_date=now,
                    last_updated_date=now)]
#    vendors = [dict(name='yahoo',
#                    website_url='http://ichart.finance.yahoo.com/table.csv?s={ticker}&a={start_month}&b={start_day}&c={start_year}&d={end_month}&e={end_day}&f={end_year}',
#                    created_date=now,
#                    last_updated_date=now)]
    update_db({'engine': engine,
               'vendor_table': reflect_table(engine, 'data_vendor'),
               'vendor_list': vendors})

