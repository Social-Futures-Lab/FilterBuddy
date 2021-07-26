import re
from .models import Channel, RuleCollection, Rule, Video, Comment, Reply

def serializeCommentWithPhrase(myComment, phrase, isComment=True):
	k = re.search(r'\b({})\b'.format(phrase), myComment.text)
	if (isComment):
		commentId = myComment.comment_id
	else:
		commentId = myComment.reply_id
	commentObject = {
		'id': commentId,
		'text': myComment.text,
		'author': myComment.author,
		'likeCount': myComment.likeCount,
		'pub_date': myComment.pub_date.strftime("%m/%d/%Y, %H:%M:%S"),
		'span': k.span()
	}
	return commentObject


def serializeComment(myComment, isComment=True):
	if (isComment):
		commentId = myComment.comment_id
	else:
		commentId = myComment.reply_id
	commentObject = {
		'id': commentId,
		'text': myComment.text,
		'author': myComment.author,
		'likeCount': myComment.likeCount,
		'pub_date': myComment.pub_date.strftime("%m/%d/%Y, %H:%M:%S"),
	}
	return commentObject

def getMatchedComments(rule, myChannel):
	phrase = rule['phrase']
	myComments = Comment.objects.filter(video__channel=myChannel)
	matched_comments = []
	for myComment in myComments:
		if (re.search(r'\b({})\b'.format(phrase), myComment.text)):
			matched_comment = serializeCommentWithPhrase(myComment, phrase, True)
			matched_comments.append(matched_comment)
		replies = Reply.objects.filter(comment=myComment)
		for reply in replies:
			if (phrase in reply.text):
				matched_comment = serializeCommentWithPhrase(reply, phrase, False)
				matched_comments.append(matched_comment)
	return matched_comments
