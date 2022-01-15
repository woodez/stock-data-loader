import pandas
import psycopg2
import yfinance as yf
import math

def insert_database(stock_ticker, number_shares):
    connection = psycopg2.connect(user="stockfi",
                                  password="jandrew28",
                                  host="postgresdb1.woodez.net",
                                  port="5432",
                                  database="stockfi")
    cursor = connection.cursor()
    cursor.execute("INSERT INTO mybag_mybag (username, stock_ticker, number_shares) VALUES(%s, %s, %s)", ("kwood", stock_ticker, number_shares))
    connection.commit()
    cursor.close()
    connection.close()



data = pandas.read_csv('woodez-quotes.csv')
symbol_list = data['Symbol'].unique()

def get_quanity(ticker):
    info = data[data['Symbol'] == ticker]
    shares = info['Quantity'].agg(['sum']) 
    results = {'ticker': ticker, 'shares': shares['sum']}
    return results
# print(symbol_list)
# print(get_quanity('SQ'))
#### total = data.groupby('Symbol')['Quantity'].agg(['sum'])
###total = data.groupby(["Symbol", "Quantity"])["Qauntity"].sum()
##tuples = list(set([tuple(x) for x in total.to_numpy()]))
# sum_total = total['
###print(type(total))
for ticker in symbol_list:
    shares = get_quanity(ticker)['shares']
    print(ticker)
    insert_database(ticker, shares)
##        postgres_insert_query = """ INSERT INTO mybag_mybag (ID, MODEL, PRICE) VALUES (%s,%s,%s)"""

#    info = data[data['Symbol'] == ticker]
#    print(info)
