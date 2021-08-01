import re
from .models import Channel, RuleCollection, Rule, Video, Comment
from collections import defaultdict
from datetime import datetime
from dateutil import parser

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
    'pub_date': myComment.pub_date.isoformat(),
    'is_comment': isComment,
    'video_id': myComment.video.video_id,
    'video_title': myComment.video.title,
    'span': k.span(),    
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
    'pub_date': myComment.pub_date.isoformat(),    
    'is_comment': isComment,    
    'video_id': myComment.video.video_id,
    'video_title': myComment.video.title,
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
  return matched_comments

def convertDate(myDate):
  newDate = datetime.strptime(myDate, '%Y-%m-%dT%H:%M:%S%z').strftime('%Y-%m-%d')    
  return newDate

def ruleDateCounter(rule_matched_comments):
  myData = defaultdict(int)
  for comment in rule_matched_comments:
    pub_date = comment['pub_date']
    pub_date = convertDate(pub_date)
    myData[pub_date] += 1

  data = []
  for pub_date in sorted(myData.keys()):
    data.append(
        {
          'x': pub_date,
          'y': myData[pub_date]
        }
      )
  return data

def getMatchedCommentsAndPrettify(rule, myChannel):
  comments = getMatchedComments(rule, myChannel)
  for comment in comments:
    comment['pub_date'] = pretty_date(comment['pub_date'])
  return comments


def pretty_date(time=False):
    """
    Get a datetime object or a int() Epoch timestamp and return a
    pretty string like 'an hour ago', 'Yesterday', '3 months ago',
    'just now', etc
    """
    
    now = datetime.now()
    time = parser.parse(time).replace(tzinfo=None)
    if type(time) is int:
        diff = now - datetime.fromtimestamp(time)
    elif isinstance(time,datetime):
        diff = now - time
    elif not time:
        diff = now - now
    second_diff = diff.seconds
    day_diff = diff.days


    if day_diff < 0:
        return ''

    if day_diff == 0:
        if second_diff < 10:
            return "just now"
        if second_diff < 60:
            return str(second_diff) + " seconds ago"
        if second_diff < 120:
            return "a minute ago"
        if second_diff < 3600:
            return str(int(second_diff / 60)) + " minutes ago"
        if second_diff < 7200:
            return "an hour ago"
        if second_diff < 86400:
            return str(int(second_diff / 3600)) + " hours ago"
    if day_diff == 1:
        return "Yesterday"
    if day_diff < 7:
        return str(day_diff) + " days ago"
    if day_diff < 14:
        return  "a week ago"        
    if day_diff < 31:
        return str(int(day_diff / 7)) + " weeks ago"
    if day_diff < 60:
        return "a month ago"        
    if day_diff < 365:
        return str(int(day_diff / 30)) + " months ago"
    return str(int(day_diff / 365)) + " years ago"