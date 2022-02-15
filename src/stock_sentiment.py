import yfinance as yf
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

userID = '@Square'
api = tweepy.API(auth)
tweets = api.user_timeline(screen_name=userID, 
                           # 200 is the maximum allowed count
                           count=200,
                           include_rts = False,
                           # Necessary to keep full_text 
                           # otherwise only the first 140 words are extracted
                           tweet_mode = 'extended'
                           )
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

def import_data_redis(alias,sentiment_data):
    cache_df(alias, sentiment_data)
## for info in tweets[:20]:
#     print("ID: {}".format(info.id))
##    created = info.created_at
##    tweet_msg = info.full_text.strip('\n')
##    print(tweet_msg)
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
    import_data_redis("ticker_sentiment",sentiment_df)
    print(sentiment_df)
    return sentiment_df

ticker_news()
# get_sentiment("PLTR")
