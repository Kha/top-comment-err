# vim:noet:sw=4:ts=4

from errbot import BotPlugin
import praw
import bs4

r = praw.Reddit(user_agent='top-comment-err 1.0 by /u/derKha')

# http://stackoverflow.com/a/520078/161659
def extractlinks(html):
	soup = bs4.BeautifulSoup(html)
	return [a['href'] for a in soup.findAll('a')]

def unescape_html(encoded):
	return bs4.BeautifulSoup(encoded).prettify(formatter=None)

MAX_LEN = 500

def get_top_comment(url):
	submissions = r.get_info(url)
	for s in sorted(submissions, key=lambda s: s.score, reverse=True):
		if s.comments:
			max_comment = max(s.comments, key=lambda c: getattr(c, 'score', -1))
			if max_comment.score > 10:
				body = unescape_html(max_comment.body_html)
				if len(body) > MAX_LEN:
					soup = bs4.BeautifulSoup(body[:MAX_LEN])
					soup.div.append(bs4.BeautifulSoup('<p><a href="{0}">...</a></p>'.format(max_comment.permalink)))
					body = str(soup)
				return body

	return None

class TopCommentErr(BotPlugin):
	def __init__(self):
		super().__init__()

	def callback_message(self, conn, mess):
		for url in extractlinks(str(mess.getHTML())):
			top_comment = get_top_comment(url)
			if top_comment:
				self.send(mess.getFrom(), top_comment, message_type=mess.getType())
				return
