import yfinance as yf
import tweepy
import sys
sys.path.append('.')
from secretget import Secret
from textblob import TextBlob
import nltk
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')

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

for info in tweets[:20]:
#     print("ID: {}".format(info.id))
    created = info.created_at
    tweet_msg = info.full_text.strip('\n')
#    print(tweet_msg)
#public_tweets = api.search_tweets(q="Square", lang="en")
# for tweet in public_tweets:
#    print(tweet.text)
#    analysis = TextBlob(tweet.text)
#    print(analysis.sentiment)

msft = yf.Ticker("SQ")
for news in msft.news:
    if "SQ" in news['title']:
       print(news['title'])