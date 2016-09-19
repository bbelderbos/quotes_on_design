from quotes import *
import mock
import unittest

class TestQuotes(unittest.TestCase):

  def setUp(self):
    self.quote = "<p>In all affairs it&#8217;s a healthy thing now and then to hang a question mark on the things you have long taken for granted.  </p>\n"
    self.squote = "This is a short code"
    self.q = {
      'title' : "some title",
      'content' : "some content",
      'link' : "http://bobbelderbos.com",
    }

  def test_get_quote(self): 
    resp = get_quote(URL)
    self.assertIsInstance(resp, dict)
    self.assertIn('content', resp)
    self.assertRaises(NoValidResponse, get_quote, "badurl")

  def test_strip_html(self):
    quote_no_html = strip_html(self.quote) 
    self.assertEqual(quote_no_html[0:6], "In all")

  def test_get_max_quote_len(self):
    max_len = get_max_quote_len(self.squote)
    self.assertEqual(max_len, 86)

  def test_html_unescape(self):
    unesc_str = html_unescape(self.quote)
    self.assertIn("it's".replace("'", u'\u2019'), unesc_str)
    self.assertNotIn("it&#8217;s", unesc_str)

  def test_create_tweet(self):
    expected_tweet = "some content - some title #quote http://bobbelderbos.com"
    self.assertEqual(create_tweet(self.q), expected_tweet)
    self.q['title'] = "some very long title" + "bla" * 1000
    self.assertRaises(TweetTooLong, create_tweet, self.q)

  # cool ... https://www.toptal.com/python/an-introduction-to-mocking-in-python
  @mock.patch.object(tweepy.API, 'update_status')
  def test_post_to_twitter(self, mock_update_status):
    ta = TwitterPost("fake auth token")
    ta.post_tweet("Hello World!")
    mock_update_status.assert_called_with("Hello World!")


if __name__ == "__main__":
  unittest.main()

