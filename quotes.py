import HTMLParser
import logging
from pprint import pprint as pp
import re
import requests
import sys
import time
import tweepy
from config import *

html_parser = HTMLParser.HTMLParser()
logging.basicConfig(filename=LOGFILE,
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.DEBUG)

class TweetTooLong(Exception):
  def __init__(self, value):
    self.value = value
  def __str__(self):
    return repr(self.value)

def get_quote(url):
  try:
    r = requests.get(url)
  except requests.exceptions.ConnectionError:
    logging.error("Cannot connect to url %s" % url)
  if not r.ok or not r.json(): 
    logging.error("Not 200 OK status for url %s" % url)
  return r.json()[0]

def strip_html(q):
  return re.sub(r'<[^<]+?>', '', q).strip()

def get_max_quote_len(title):
  return TWEET_LEN - SHORT_URL_LEN - len(title) - len(ELLIPSIS) - len(TAG)

def html_unescape(tw):
  return html_parser.unescape(tw)

def create_tweet(q):
  title = " - %s " % q['title']
  qlen = get_max_quote_len(title)
  quote = strip_html(q['content'])
  if len(quote) > qlen:
    quote = quote[0:qlen] + ELLIPSIS
  tw = [quote, title, TAG]
  if len("".join(tw)) > (TWEET_LEN - SHORT_URL_LEN):
    raise TweetTooLong("Tweet cannot be longer than %d chars" % TWEET_LEN)
  return html_unescape("".join(tw + [q['link']]))

def get_twitter_api():
  auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
  auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
  return tweepy.API(auth)


if __name__ == "__main__":
  url = "http://quotesondesign.com/wp-json/posts?filter[orderby]=rand" # api-v4-0
  num_tweets = 1
  # allow for more than one tweet
  if len(sys.argv) > 1:
    num_tweets = sys.argv[1]
    try:
      num_tweets = int(num_tweets)
    except ValueError:
      sys.exit("Please provide numeric first cli arg")
  tweets = []
  for i in range(num_tweets):
    tw = None
    try:
      tw = create_tweet(get_quote(url))
    except TweetTooLong as e:
      logging.warning(e)
      continue
    tweets.append(tw)

  api = get_twitter_api()
  for tw in tweets:
    api.update_status(tw) 
    time.sleep(2)
