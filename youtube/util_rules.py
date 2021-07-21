import re
from .models import Channel, RuleCollection, Rule, Video, Comment, Reply

def serializeComment(myComment, phrase):
	k = re.search(r'\b({})\b'.format(phrase), myComment.text)
	commentObject = {
		'id': myComment.id,
		'text': myComment.text,
		'author': myComment.author,
		'likeCount': myComment.likeCount,
		'pub_date': myComment.pub_date.strftime("%m/%d/%Y, %H:%M:%S"),
		'span': k.span()
	}
	return commentObject


def serializeComment(myComment):
	commentObject = {
		'id': myComment.id,
		'text': myComment.text,
		'author': myComment.author,
		'likeCount': myComment.likeCount,
		'pub_date': myComment.pub_date.strftime("%m/%d/%Y, %H:%M:%S"),
	}
	return commentObject

def getMatchedComments(rule, myChannel):
	phrase = rule.phrase
	myComments = Comment.objects.filter(video__channel=myChannel)
	matched_comments = []
	for myComment in myComments:
		if (phrase in myComment.text):
			matched_comment = serializeComment(myComment, phrase)
			matched_comments.append(matched_comment)
		replies = Reply.objects.filter(comment=myComment)
		for reply in replies:
			if (phrase in reply.text):
				matched_comment = serializeComment(reply, phrase)
				matched_comments.append(matched_comment)
	return matched_comments
