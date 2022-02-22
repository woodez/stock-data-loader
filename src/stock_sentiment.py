import yfinance as yf
from datetime import datetime
import tweepy
import sys
sys.path.append('.')
from secretget import Secret
from textblob import TextBlob
import nltk
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
import psycopg2
import yfinance as yf
import math
import pyarrow as pa
import pandas as pd
import redis
import warnings
warnings.filterwarnings("ignore")

con_secret = Secret()
twitter_auth = con_secret.get_secret('code/code/stockfi/twitter').get('data')
consumer_key = twitter_auth['APIKey']
consumer_secret = twitter_auth['APIKeySecret']
access_token = twitter_auth['AccessToken']
access_token_secret = twitter_auth['AccessTokenSecret']

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

def twitter_query(userID):
    # userID = '@BTCTN'
    api = tweepy.API(auth)
    tweets = api.user_timeline(screen_name=userID, 
                               # 200 is the maximum allowed count
                               count=200,
                               include_rts = False,
                               # Necessary to keep full_text 
                               # otherwise only the first 140 words are extracted
                               tweet_mode = 'extended'
                               )
    return tweets

def twitter_query_crisis(search_string):
    api = tweepy.API(auth)
    public_tweets = api.search_tweets(q=search_string, count=100, tweet_mode = 'extended', lang="en")
    return public_tweets


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

def import_data_redis(alias,sentiment_data):
    cache_df(alias, sentiment_data)

def twitter_sentiment(twitter_user,datasource,type):
    sentiment_total = 0
#     tweets = twitter_query("@BTCTN")
    if "crisis" in type:
       tweets = twitter_query_crisis("Ukraine")
    else:
       tweets = twitter_query(twitter_user)

    for info in tweets[:40]:
#        print("ID: {}".format(info.id))
        created = info.created_at
        tweet_msg = info.full_text.strip('\n')
        analysis = TextBlob(str(tweet_msg))
        sentiment = analysis.sentiment.polarity
#        print("{},{}".format(tweet_msg,sentiment))
        sentiment_total+=sentiment
    test = redis_set(sentiment_total,datasource)
    print(test)


def redis_set(total,data):
    portfolio_dates = []
    value_list = []
    today = datetime.today().strftime('%m/%d/%Y')
    value = '{:.2f}'.format(total)
    portfolio_dates.append(today)
    value_list.append(value)
    df_new = pd.DataFrame({'date': portfolio_dates, 'value': value_list})
    try:
       df_redis = get_cached_df(data)
       df_redis = df_redis.append(df_new, ignore_index = True )
       df_redis.drop_duplicates(subset ="date", keep = "last", inplace = True)
    except TypeError:
       df_redis = df_new
    
    import_data_redis(data,df_redis)
    # import_data_redis("ticker_sentiment",sentiment_df)        
    return df_redis
 

##    public_tweets = api.search_tweets(q="Square", lang="en")
# for tweet in public_tweets:
#    print(tweet.text)
#    analysis = TextBlob(tweet.text)
#    print(analysis.sentiment)



def get_sentiment(ticker):
    ticker = yf.Ticker(ticker)
    sentiment_total = 0
    for news in ticker.news:
        analysis = TextBlob(str(news['title']))
        sentiment = analysis.sentiment.polarity
        sentiment_total+=sentiment
    return sentiment_total

def ticker_news():
    records = get_data_db("select * from mybag_mybag")
    sentiment_list = {}
    for row in records:
       ticker = row[2]
       if '-' in ticker:
          ticker = ticker.split("-")[0].upper()
       elif '.' in ticker:
          ticker = ticker.split(".")[0].upper()
       else:
          ticker = ticker.upper()

       if "BTC" not in ticker and "ETH" not in ticker:
          sentiment = get_sentiment(ticker)
          tmpdict = { ticker : sentiment }
          sentiment_list.update(tmpdict)

    ticker_list = []
    value_list = []
    for key, value in sentiment_list.items():
        ticker_list.append(key)
        value_list.append(value)
    sentiment_details = {
        'Name': ticker_list,
        'Amount': value_list,
    }
    sentiment_df = pd.DataFrame(sentiment_details)
    total = math.fsum(value_list)
    portfolio_dates = []
    value_list = []
    today = datetime.today().strftime('%m/%d/%Y')
    value = '{:.2f}'.format(total)
    portfolio_dates.append(today)
    value_list.append(value)
    df_new = pd.DataFrame({'date': portfolio_dates, 'value': value_list})
    try:
       df_redis = get_cached_df("woodez_sentiment")
       df_redis = df_redis.append(df_new, ignore_index = True )
       df_redis.drop_duplicates(subset ="date", keep = "last", inplace = True)
    except TypeError:
       df_redis = df_new
    print(df_redis)
    import_data_redis("woodez_sentiment",df_redis)
    # import_data_redis("ticker_sentiment",sentiment_df)    
    return sentiment_df

ticker_news()
twitter_sentiment("@BTCTN", "btc_sentiment","NA")
twitter_sentiment("@markets","market_sentiment","NA")
twitter_sentiment("NA","war_sentiment","crisis")
# test = twitter_query_crisis("Ukraine")
# sentiment_total = 0
# for info in test[:40]:
#    created = info.created_at
#    tweet_msg = info.full_text.strip('\n')
#    analysis = TextBlob(str(tweet_msg))
#    sentiment = analysis.sentiment.polarity
#    sentiment_total+=sentiment
# print(sentiment_total)

# get_sentiment("PLTR")
