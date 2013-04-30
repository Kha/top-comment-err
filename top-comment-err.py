# vim:noet:sw=4:ts=4

from errbot import BotPlugin
import praw
import bs4

r = praw.Reddit(user_agent='top-comment-err 1.0 by /u/derKha')

# http://stackoverflow.com/a/520078/161659
def extractlinks(html):
	soup = bs4.BeautifulSoup(html)
	return [a['href'] for a in soup.findAll('a')]

def get_top_comment(url):
	submissions = r.get_info(url)
	if submissions:
		comments = submissions[0].comments # sorted by score, apparently
		if comments:
			return comments[0].body # dito
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
