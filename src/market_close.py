from datetime import datetime
import psycopg2
import yfinance as yf
import math
import pyarrow as pa
import pandas as pd
import redis
import warnings
warnings.filterwarnings("ignore")


def get_day_open(ticker):
    ticker = "{}-trend".format(ticker) 
    return '{:.2f}'.format(float(get_cached_df(ticker)['Open'].iloc[:1][0]))


def get_cached_df(alias):
    pool = redis.ConnectionPool(host='redis01.woodez.net',port='6379', db=0) 
    cur = redis.Redis(connection_pool=pool)
    context = pa.default_serialization_context()
    result = cur.get(alias)
    dataframe = pd.DataFrame.from_dict(context.deserialize(result))
    return dataframe

def cache_df(alias,df):
    pool = redis.ConnectionPool(host='redis01.woodez.net', port='6379', db=0)
    cur = redis.Redis(connection_pool=pool)
    context = pa.default_serialization_context()
    df_compressed =  context.serialize(df).to_buffer().to_pybytes()
    res = cur.set(alias,df_compressed)

def import_data_redis(alias,close_data):
    cache_df(alias, close_data)


def get_data_db(query):
    connection = psycopg2.connect(user="stockfi",
                                  password="jandrew28",
                                  host="postgresdb1.woodez.net",
                                  port="5432",
                                  database="stockfi")
    cursor = connection.cursor()
    cursor.execute(query)
    records = cursor.fetchall()
    return records



def current_portfolio_value():
    records = get_data_db("select * from mybag_mybag")
    close_list = {}
    for row in records:
       ticker = row[2]
       if '-' in ticker:
          ticker = ticker.split("-")[0].upper()
       elif '.' in ticker:
          ticker = ticker.split(".")[0].upper()
       else:
          ticker = ticker.upper()

       if "BTC" not in ticker and "ETH" not in ticker:
          close = get_day_open(ticker)
          tmpdict = { ticker : close }
          close_list.update(tmpdict)

    ticker_list = []
    value_list = []
    for key, value in close_list.items():
        ticker_list.append(key)
        value_list.append(value)
    close_details = {
        'Name': ticker_list,
        'Amount': value_list,
    }
    close_df = pd.DataFrame(close_details)
    import_data_redis("ticker_close",close_df)
    print(close_df)
    return close_df

current_portfolio_value()
