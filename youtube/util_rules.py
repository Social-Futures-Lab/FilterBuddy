import re
from .models import Channel, RuleCollection, Rule, Video, Comment
from collections import defaultdict
from datetime import datetime, timedelta
from dateutil import parser

t_col = "#235dba"
c_col = "#a50808"
g_col = "#005916"
r_col = "#ff9900"
black = "#000000"
pink = "#f442f1"

NUM_DAYS_IN_CHARTS = 30
CHARTS_START_DATE = datetime.now() - timedelta(NUM_DAYS_IN_CHARTS)

def getColors(n):
  colors = [t_col, c_col, g_col, r_col, black, 'c', 'm', pink]
  while (len(colors) < n):
    colors = colors + shuffle(colors)  
  colors = colors[:n]
  return colors

def serializeCommentWithPhrase(myComment, phrase):
  k = re.search(r'\b({})\b'.format(phrase), myComment.text)
  commentObject = {
    'id': myComment.comment_id,
    'text': myComment.text,
    'author': myComment.author,
    'likeCount': myComment.likeCount,
    'pub_date': myComment.pub_date.isoformat(),
    'video_id': myComment.video.video_id,
    'video_title': myComment.video.title,
    'span': k.span(),    
  }
  return commentObject


def serializeComment(myComment):
  commentObject = {
    'id': myComment.comment_id,
    'text': myComment.text,
    'author': myComment.author,
    'likeCount': myComment.likeCount,
    'pub_date': myComment.pub_date.isoformat(),    
    'video_id': myComment.video.video_id,
    'video_title': myComment.video.title,
  }
  return commentObject

def getMatchedComments(rule, myChannel):
  phrase = rule['phrase']
  myCollections = RuleCollection.objects.filter(owner = myChannel)
  myComments = Comment.objects.filter(video__channel=myChannel)
  matched_comments = []
  for myComment in myComments:
    if (re.search(r'\b({})\b'.format(phrase), myComment.text)):
      matched_comment = serializeCommentWithPhrase(myComment, phrase)
      matched_comment['catching_collection'] = getCatchingCollection(myComment, myCollections)    
      matched_comments.append(matched_comment)
  return matched_comments

def getMatchedCommentsForCharts(rule, myChannel):
  phrase = rule['phrase']
  myComments = Comment.objects.filter(video__channel = myChannel, pub_date__gte = CHARTS_START_DATE)
  matched_comments = []
  for myComment in myComments:
    if (re.search(r'\b({})\b'.format(phrase), myComment.text)):
      matched_comment = serializeCommentWithPhrase(myComment, phrase)
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
  # for pub_date in sorted(myData.keys()):
  for pub_date in (CHARTS_START_DATE + timedelta(n) for n in range(NUM_DAYS_IN_CHARTS + 1)):
    pub_date = pub_date.strftime('%Y-%m-%d')    
    data.append(
        {
          'x': pub_date,
          'y': myData[pub_date]
        }
      )
  return data

def getChannel(request):
  if 'credentials' in request.session and 'myChannelId' in request.session['credentials']:
    myChannelId = request.session['credentials']['myChannelId']
    myChannel = Channel.objects.get(channel_id = myChannelId)
    return myChannel
  else:
    #return makeDebugChannel()
    raise Exception('Could not get login credentials')  

def get_matched_comment_ids(myChannelComments, rules):    
  matched_comment_ids = []
  for comment in myChannelComments:
    lookups = []
    for rule in rules:
      rule_phrase = rule.get_phrase()
      if (rule.case_sensitive):
        lookup = re.search(r'\b({})\b'.format(rule_phrase), comment.text)
      else:
        lookup = re.search(r'\b({})\b'.format(rule_phrase), comment.text, re.IGNORECASE)
      lookups.append(lookup)
    if any(lookups):
      matched_comment_ids.append(comment.id)  
  return matched_comment_ids    

def getCatchingCollection(comment, myCollections):
  for collection in myCollections:
    rules = Rule.objects.filter(rule_collection = collection)
    lookups = []
    for rule in rules:
      rule_phrase = rule.get_phrase()
      if (rule.case_sensitive):
        lookup = re.search(r'\b({})\b'.format(rule_phrase), comment.text)
      else:
        lookup = re.search(r'\b({})\b'.format(rule_phrase), comment.text, re.IGNORECASE)
      lookups.append(lookup)
    if any(lookups):
      return collection.name
  return None    

  return comment.pub_date.isoformat()

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