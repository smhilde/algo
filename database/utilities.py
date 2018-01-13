import sqlalchemy as sql

db_info = {'user': 'quant',
           'password': 'na442h16',
           'host': 'localhost',
           'db': 'securities_master'}

def reflect_table(engine, table):
    return sql.Table(table, sql.MetaData(), autoload=True, autoload_with=engine)

def insert(engine, table, values):
    with engine.connect() as conn:
        res = conn.execute(sql.insert(table), values)
    print('Inserted {} values in to {!r}. {} values expected.'.format(res.rowcount,
                                                                      table.name,
                                                                      len(values)))
def create_engine(db_info=db_info):
    return sql.create_engine('mysql+mysqldb://{user}:{password}@{host}/{db}'.format(**db_info))
