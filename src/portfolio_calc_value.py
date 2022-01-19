from datetime import datetime
import psycopg2
import yfinance as yf
import math
import pyarrow as pa
import pandas as pd
import redis
import warnings
warnings.filterwarnings("ignore")

def cache_df(alias,df):
    pool = redis.ConnectionPool(host='redis01.woodez.net', port='6379', db=0)
    cur = redis.Redis(connection_pool=pool)
    context = pa.default_serialization_context()
    df_compressed =  context.serialize(df).to_buffer().to_pybytes()
    res = cur.set(alias,df_compressed)

def get_cached_df(alias):
    pool = redis.ConnectionPool(host='redis01.woodez.net',port='6379', db=0) 
    cur = redis.Redis(connection_pool=pool)
    context = pa.default_serialization_context()
    result = cur.get(alias)
    dataframe = pd.DataFrame.from_dict(context.deserialize(result))
    return dataframe

def get_close_value(ticker):
    data = yf.Ticker(ticker).info
    return data['regularMarketPrice']

def import_data_redis(alias,portfolio_data):
    cache_df(alias, portfolio_data)


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
    portfolio_list = {}
    for row in records:
       ticker = row[2]
       amount = row[3]
       tmpdict = { ticker : amount }
       portfolio_list.update(tmpdict)

    value_list = []
    for key, value in portfolio_list.items():
        price = get_close_value(key)
        market_value = float(price) * float(value)
        value_list.append(market_value)
    total = math.fsum(value_list)
    portfolio_dates = []
    value_list = []
    today = datetime.today().strftime('%m/%d/%Y')
    value = '{:.2f}'.format(total)
    print(today)
    portfolio_dates.append(today)
    value_list.append(value)
    df_new = pd.DataFrame({'date': portfolio_dates, 'value': value_list}) 
    try:
       df_redis = get_cached_df("woodez")
       df_redis = df_redis.append(df_new, ignore_index = True )
       df_redis.drop_duplicates(subset ="date", keep = "last", inplace = True)
    except TypeError:
       print("what") 
       df_redis = df_new    
    import_data_redis("woodez",df_redis)
    return df_redis

#print('{:.2f}'.format(total))
current_portfolio_value()
print("##########Storing Woodez Fund Value###############")       
print(get_cached_df("woodez"))
# print(current_portfolio_value())
# current_portfolio_value()
###df_redis = get_cached_df("woodez")
###print(type(df_redis))
###df_redis.drop_duplicates(subset ="date", keep = "last", inplace = True)
###print(df_redis)
