import re
from .models import Channel, RuleCollection, Rule, Video, Comment, Reply

t_col = "#235dba"
c_col = "#a50808"
g_col = "#005916"
r_col = "#ff9900"
black = "#000000"
pink = "#f442f1"

def getColors(n):
  colors = [t_col, c_col, g_col, r_col, black, 'c', 'm', pink]
  while (len(colors) < n):
    colors = colors + shuffle(colors)  
  colors = colors[:n]
  return colors

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
  if (phrase == ''):
    return []
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
