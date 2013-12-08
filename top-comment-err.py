# vim:noet:sw=4:ts=4

from errbot import BotPlugin, botcmd
import praw
import bs4
import random

r = praw.Reddit(user_agent='top-comment-err 1.0 by /u/derKha')

# http://stackoverflow.com/a/520078/161659
def extractlinks(html):
	soup = bs4.BeautifulSoup(html)
	return [a['href'] for a in soup.findAll('a')]

def unescape_html(encoded):
	return bs4.BeautifulSoup(encoded).prettify(formatter=None)

MAX_LEN = 500

def format_comment_body(comment):
	body = unescape_html(comment.body_html)
	if len(body) > MAX_LEN:
		soup = bs4.BeautifulSoup(body[:MAX_LEN])
		soup.div.append(bs4.BeautifulSoup('<p><a href="{0}">...</a></p>'.format(comment.permalink)))
		body = str(soup)
	return body

def get_top_comment(url):
	submissions = r.get_info(url)
	for s in sorted(submissions, key=lambda s: s.score, reverse=True):
		if s.comments:
			max_comment = max(s.comments, key=lambda c: getattr(c, 'score', -1))
			if max_comment.score > 10:
				return format_comment_body(max_comment)

	return None

def get_top(subreddit):
	# some praw bug, I don't care
	res = []
	try:
		for submission in r.get_top(subreddit):
			res.append(submission)
	except TypeError:
		pass
	return res

class TopCommentErr(BotPlugin):
	def __init__(self):
		super().__init__()

	def callback_message(self, conn, mess):
		for url in extractlinks(str(mess.getHTML())):
			top_comment = get_top_comment(url)
			if top_comment:
				self.send(mess.getFrom(), top_comment, message_type=mess.getType())
				return

	@botcmd
	def bored(self, mess, args):
		submissions = [s for s in r.get_subreddit('AskReddit').get_top(params={'t': 'week'}) if s.num_comments > 5000 and not s.over_18]
		if submissions:
			s = random.choice(submissions)
			comments = [c for c in s.comments if getattr(c, 'score', -1) > 300]
			if comments:
				c = random.choice(comments)
				return '<div><b>{}</b><br/>{}</div>'.format(s.title, format_comment_body(c))
