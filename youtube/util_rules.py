import re
from .models import Channel, RuleCollection, Rule, Video, Comment
from collections import defaultdict
from datetime import datetime, timedelta
from dateutil import parser
from random import sample

t_col = "#235dba"
c_col = "#a50808"
g_col = "#005916"
r_col = "#ff9900"
black = "#000000"
dg_color = "#097f8c"
pink = "#f442f1"
ly_color = "#ffce00"
sb_color = "#00aaff"
lp_color = "#cec6f7"

NUM_DAYS_IN_CHARTS = 30
CHARTS_START_DATE = datetime.now() - timedelta(NUM_DAYS_IN_CHARTS)

def getColors(n):
  colors = [t_col, c_col, g_col, r_col, black, dg_color, pink, ly_color, sb_color, lp_color]
  while (len(colors) < n):
    colors = colors + sample(colors, len(colors))
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

#def getMatchedCommentsForOverviewChart(filter_rule, myChannel):
  # Security options
    # 1. Check if rule is a part of myChannel and fail if not
    # 2. Join with a smaller table (Rule or Channel) - joins are more but tables are smaller

  # TODO: will this work? Seems to be converting Rule to a dictionary in unified rule... can I add field
  # for channel id in rule? (RuleCollection owner)
  # Just use a query

  # get all rules for channel
#  containsRule = False
#  collections = RuleCollection.objects.filter(owner = myChannel)
#  for collection in collections:
#    rules = Rule.objects.filter(rule_collection = collection)
#    # check to see if current rule is in channel
#    if (rules.contains(filter_rule) == True):
#      containsRule = True
#  if (containsRule == False):
#    return


  # for storing matched comment objects
#  matched_comments = []
  # get matched comments for the rule
#  comments = MatchedComments.objects.filter(rule_id = filter_rule.id, applied_date__gte = CHARTS_START_DATE)
  # comments = MatchedComments.objects.filter(rule__id = filter_rule.id, comment__video__channel = myChannel, comment__pub_date__gte = CHARTS_START_DATE).select_related("Comment")
  # comments = MatchedComments.objects.filter(rule = filter_rule.id, applied_date__gte = CHARTS_START_DATE)
  # rule__id or rule__pk
#  for c in comments:
    # store the comment
    # TODO: change pub_date to applied date (ruleDateCounter method below) (?)
#    match = {
#      'id': c.comment_id,
#      'pub_date': c.applied_date.isoformat(),
#    }
#    matched_comments.append(match)
  # return list
#  return matched_comments

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
  #newDate = datetime.strptime(myDate, '%Y-%m-%dT%H:%M:%S%z').strftime('%Y-%m-%d')
  newDate = datetime.strptime(myDate, '%Y-%m-%dT%H:%M:%S.%f%z').strftime('%Y-%m-%d')
  return newDate

def ruleDateCounter(rule_matched_comments):
  myData = defaultdict(int)
  for comment in rule_matched_comments:
    applied_date = comment['applied_date']
    applied_date = convertDate(applied_date)
    myData[applied_date] += 1

  data = []
  for applied_date in (CHARTS_START_DATE + timedelta(n) for n in range(NUM_DAYS_IN_CHARTS + 1)):
        applied_date = applied_date.strftime('%Y-%m-%d')
        data.append(
          {
            'x': applied_date,
            'y': myData[applied_date]
          }
        )
  return data

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
