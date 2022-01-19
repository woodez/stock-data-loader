from datetime import datetime
import psycopg2
import yfinance as yf
import math
import pyarrow as pa
import pandas as pd
import redis
from matplotlib import pyplot as plt
import numpy as np
import warnings

warnings.filterwarnings("ignore")


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


records = get_data_db("select * from mybag_mybag")
portfolio_list = {}
for row in records:
    ticker = row[2]
    amount = row[3]
    tmpdict = { ticker : amount }
    portfolio_list.update(tmpdict)

tickers = []
volume = []
for line in portfolio_list.keys():
    if portfolio_list[line] != 0:
       tickers.append(line)
       volume.append(portfolio_list[line])

details = {
    'Name': tickers,
    'Amount': volume,
}

df = pd.DataFrame(details)

print(df['Name'][0])
fig = plt.figure(figsize =(10, 7))
plt.pie(df['Amount'], labels = df['Name'])
plt.show()
