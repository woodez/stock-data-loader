import pyarrow as pa
import redis
import yfinance as yf
import sys
import warnings
warnings.filterwarnings("ignore")

# ticker = yf.Ticker("BTC-CAD")
# import_df = ticker.history(period="max")
# print(import_df)

def cache_df(alias,df):
    pool = redis.ConnectionPool(host='redis01.woodez.net', port='6379', db=0)
    cur = redis.Redis(connection_pool=pool)
    context = pa.default_serialization_context()
    df_compressed =  context.serialize(df).to_buffer().to_pybytes()

    res = cur.set(alias,df_compressed)
    if res == True:
        print('df cached')


ticker = yf.Ticker("BTC-CAD")
import_df = ticker.history(period="max")
cache_df("BTC-CAD-HIST", import_df)
print(import_df)

ticker = yf.Ticker("ETH-CAD")
import_df = ticker.history(period="max")
cache_df("ETH-CAD-HIST", import_df)
print(import_df)

df = yf.download(tickers="BTC-CAD",period='7d',interval='1m')
cache_df("BTC-CAD", df)
print(df)

df = yf.download(tickers="ETH-CAD",period='7d',interval='1m')
cache_df("ETH-CAD", df)
print(df)