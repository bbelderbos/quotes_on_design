import re
import requests
import sys

QUOTE_API = "http://quotesondesign.com/wp-json/posts?filter[orderby]=rand"
TWEET_LEN = 140 
SHORT_URL_LEN = 23 
ELLIPSIS = " ..."
TAG = "#quote "
HTML_TAG = re.compile(r'<[^<]+?>')

class TweetTooLong(Exception):
  def __init__(self, value):
    self.value = value
  def __str__(self):
    return repr(self.value)

def get_quote():
  r = requests.get(QUOTE_API)
  if not r.ok or not r.json(): 
    sys.exit("cannot get quote from API")
  return r.json()[0]

def strip_html(q):
  return HTML_TAG.sub('', q).strip()

def get_max_quote_len(title):
  return TWEET_LEN - SHORT_URL_LEN - len(title) - len(ELLIPSIS) - len(TAG)

def create_tweet(q):
  title = " - %s " % q['title']
  qlen = get_max_quote_len(title)
  quote = strip_html(q['content'])
  if len(quote) > qlen:
    quote = quote[0:qlen] + ELLIPSIS
  tw = [quote, title, TAG]
  if len("".join(tw)) > (TWEET_LEN - SHORT_URL_LEN):
    raise TweetTooLong("Tweet cannot be longer than %d chars" % TWEET_LEN)
  return "".join(tw + [q['link']])

if __name__ == "__main__":
  try:
    tweet = create_tweet(get_quote())
    print tweet
  except TweetTooLong as e:
    print e
    sys.exit(1)
