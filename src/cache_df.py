import pyarrow as pa
import redis
import yfinance as yf
import sys
import warnings
warnings.filterwarnings("ignore")

symbols = sys.argv[1]


def cache_df(alias,df):
    pool = redis.ConnectionPool(host='redis01.woodez.net', port='6379', db=0)
    cur = redis.Redis(connection_pool=pool)
    context = pa.default_serialization_context()
    df_compressed =  context.serialize(df).to_buffer().to_pybytes()

    res = cur.set(alias,df_compressed)
    if res == True:
        print('df cached')


def import_data_redis(alias,stock_symbol):
    ticker = yf.Ticker(stock_symbol)
    import_df = ticker.history(period="max")
    print(import_df)
    cache_df(alias, import_df)

# symbols = ["HOOD", "ETH-CAD", "BTC-CAD", "UBER", "TSLA", "SBUX", "BAC", "HHC", "PLTR", "BYL.TO", "BBD-B.TO", "NOK", "NPI.TO", "GILD", "DAL", "SNAP", "DIS", "MSFT", "SQ", "AER", "WYNN"]

# symbols = "HOOD,ETH-CAD,BTC-CAD,UBER,TSLA,SBUX,BAC,HHC,PLTR,BYL.TO,BBD-B.TO,NOK,NPI.TO,GILD,DAL,SNAP,DIS,MSFT,SQ,AER,WYNN"


for tick in symbols.split(","):
    if '-' in tick:
       alias = tick.split("-")[0].upper()
    elif '.' in tick:
       alias = tick.split(".")[0].upper()
    else:
       alias = tick.upper()
    print(alias)
    import_data_redis(alias,tick)

