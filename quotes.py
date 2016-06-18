#!/usr/bin/env python
import HTMLParser
import logging
import re
import requests
import sys
import time
import tweepy
from config import *
from exceptions import *

html_parser = HTMLParser.HTMLParser()
logging.basicConfig(filename=LOGFILE,
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.DEBUG)

def get_quote(url):
  try:
    r = requests.get(url)
    return r.json()[0]
  except:
    raise NoValidResponse("Cannot get quote from url %s" % url)

def strip_html(q):
  return re.sub(r'<[^<]+?>', '', q).strip()

def get_max_quote_len(title):
  return TWEET_LEN - SHORT_URL_LEN - len(title) - len(ELLIPSIS) - len(TAG)

def html_unescape(s):
  return html_parser.unescape(s)

def create_tweet(q):
  title = " - %s " % q['title']
  qlen = get_max_quote_len(title)
  quote = strip_html(q['content'])
  if len(quote) > qlen:
    quote = quote[0:qlen] + ELLIPSIS
  tweet = "".join([html_unescape(quote), html_unescape(title), TAG])
  if len(tweet) > (TWEET_LEN - SHORT_URL_LEN):
    raise TweetTooLong("Tweet cannot be longer than %d chars" % TWEET_LEN)
  return tweet + q['link']

def get_twitter_api():
  auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
  auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
  return tweepy.API(auth)


if __name__ == "__main__":
  url = "http://quotesondesign.com/wp-json/posts?filter[orderby]=rand" # api-v4-0
  tweets = []
  num_tweets = 1

  if len(sys.argv) > 1:
    num_tweets = sys.argv[1]
    try:
      num_tweets = int(num_tweets)
    except ValueError:
      sys.exit("Please provide numeric value for 'number of tweets'")

  for i in range(num_tweets):
    quote = tweet = None
    try:
      quote = get_quote(url)
    except NoValidResponse as e:
      logging.error(e)
    if quote: 
      try:
        tweet = create_tweet(quote)
        tweets.append(tweet)
      except TweetTooLong as e:
        logging.error(e)

  api = get_twitter_api()
  for tweet in tweets:
    api.update_status(tweet)
    time.sleep(2)
