import sqlalchemy as sql
from sqlalchemy.dialects import mysql

engine = sql.create_engine('mysql+mysqldb://quant:na442h16@localhost/securities_master')
conn = engine.connect()
meta = sql.MetaData()
meta.drop_all(engine)

exchange = sql.Table('exchange', meta,
                sql.Column('id', mysql.INTEGER(), primary_key=True),
                sql.Column('abbrev', mysql.VARCHAR(32), nullable=False),
                sql.Column('name', mysql.VARCHAR(255), nullable=False),
                sql.Column('city', mysql.VARCHAR(255), nullable=True),
                sql.Column('country', mysql.VARCHAR(255), nullable=True),
                sql.Column('currency', mysql.VARCHAR(64), nullable=True),
                sql.Column('timezone_offset', mysql.TIME, nullable=True),
                sql.Column('created_date', mysql.DATETIME(), nullable=False),
                sql.Column('last_updated_date', mysql.DATETIME(), nullable=False),
                mysql_engine='InnoDB',
                mysql_charset='utf8')

data_vendor = sql.Table('data_vendor', meta,
                sql.Column('id', mysql.INTEGER(), primary_key=True),
                sql.Column('name', mysql.VARCHAR(64), nullable=False),
                sql.Column('website_url', mysql.VARCHAR(255), nullable=True),
                sql.Column('support_email', mysql.VARCHAR(255), nullable=True),
                sql.Column('created_date', mysql.DATETIME(), nullable=False),
                sql.Column('last_updated_date', mysql.DATETIME(), nullable=False),
                mysql_engine='InnoDB',
                mysql_charset='utf8')

symbol = sql.Table('symbol', meta,
                sql.Column('id', mysql.INTEGER(), primary_key=True),
                sql.Column('exchange_id', mysql.INTEGER(), sql.ForeignKey('exchange.id'), nullable=True),
                sql.Column('ticker', mysql.VARCHAR(32), nullable=False),
                sql.Column('instrument', mysql.VARCHAR(64), nullable=False),
                sql.Column('name', mysql.VARCHAR(255), nullable=True),
                sql.Column('sector', mysql.VARCHAR(255), nullable=True),
                sql.Column('currency', mysql.VARCHAR(32), nullable=True),
                sql.Column('created_date', mysql.DATETIME(), nullable=False),
                sql.Column('last_updated_date', mysql.DATETIME(), nullable=False),
                mysql_engine='InnoDB',
                mysql_charset='utf8')

daily_price = sql.Table('daily_price', meta,
                sql.Column('id', mysql.INTEGER(), primary_key=True),
                sql.Column('data_vendor_id', mysql.INTEGER(), sql.ForeignKey('data_vendor.id'), nullable=False),
                sql.Column('symbol_id', mysql.INTEGER(), sql.ForeignKey('symbol.id'), nullable=False),
                sql.Column('price_date', mysql.DATETIME(), nullable=False),
                sql.Column('created_date', mysql.DATETIME(), nullable=False),
                sql.Column('last_updated_date', mysql.DATETIME(), nullable=False),
                sql.Column('open_price', mysql.DECIMAL(19,4), nullable=True),
                sql.Column('high_price', mysql.DECIMAL(19,4), nullable=True),
                sql.Column('low_price', mysql.DECIMAL(19,4), nullable=True),
                sql.Column('close_price', mysql.DECIMAL(19,4), nullable=True),
                sql.Column('adj_close_price', mysql.DECIMAL(19,4), nullable=True),
                sql.Column('volume', mysql.BIGINT(), nullable=True),
                mysql_engine='InnoDB',
                mysql_charset='utf8')

meta.create_all(engine)
print(engine.table_names())               
