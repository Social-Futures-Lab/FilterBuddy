# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.views.generic import TemplateView
from django.http import HttpResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from .utils import getChannelFromRequest
from .util_rules import getMatchedComments, getMatchedCommentsForCharts, getMatchedCommentsAndPrettify, serializeComment, serializeCommentWithPhrase, getColors, ruleDateCounter, get_matched_comment_ids
from .util_filters import serializeRule, serializeRules, serializeCollection
from .models import Channel, RuleCollection, Rule, Video, Comment, RuleColTemplate

from datetime import datetime, timedelta
import urllib.request, json
import random
import re
from heapq import nlargest
import os
import string

from rest_framework import viewsets
from .serializers import RuleCollectionSerializer, CommentSerializer, AllCommentsSerializer

NUM_CHART_ENTRIES = 8

def indexRuleCollection(request):
    return render(request, 'youtube/ruleCollections.html')

class RuleCollectionViewSet(viewsets.ModelViewSet):
    queryset = RuleCollection.objects.all().order_by('create_date')
    serializer_class = RuleCollectionSerializer

    def get_queryset(self):
      queryset = self.queryset
      myChannel = getChanne(self.request)
      query_set = queryset.filter(owner = myChannel)
      return query_set

def indexCommentCollection(request, filter_id):
    return render(request, 'youtube/commentsTable.html', {'filter_id': filter_id})

class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all().order_by('pub_date')
    serializer_class = CommentSerializer

    def get_queryset(self):
      queryset = self.queryset
      myChannel = getChannelFromRequest(self.request)
      myChannelComments = queryset.filter(video__channel = myChannel)

      rule_collection_id = self.kwargs['username']
      rules = Rule.objects.filter(rule_collection__id = rule_collection_id)

      matched_comment_ids = get_matched_comment_ids(myChannelComments, rules)
      matched_comments = Comment.objects.filter(id__in = matched_comment_ids)
      return matched_comments

class AllCommentsViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all().order_by('pub_date')
    serializer_class = AllCommentsSerializer

    def get_queryset(self):
      queryset = self.queryset
      myChannel = getChannelFromRequest(self.request)
      myChannelComments = queryset.filter(video__channel = myChannel)
      return myChannelComments

def isLoggedIn(request):
  return True #request.user.is_authenticated

def createChartConfig():
  # TODO make this really work
  return {
    'type': 'bar',
    'data': {
      'foo': [1, 2, 3, 4],
      'bar': [5, 6, 7, 8]
    },
    'label': 'This is fake data',
    'bgColor': '#fff',
    'borderColor': '#f00'
  }

def unifiedRule(rule):
  if type(rule) is dict:
    return rule
  elif type(rule) is Rule:
    return {
      'id': rule.id,
      'phrase': rule.phrase
    }
  else:
    raise Error('Unknown type for rule')

# @csrf_exempt
# def debug(request):
#   channel_id = ''
#   try:
#     request_data = json.loads(request.body.decode('utf-8'))
#     channel_id = request_data['channel']
#   except:
#     pass
#   channel = makeDebugChannel(channel_id = channel_id)
#   if not 'credentials' in request.session:
#     request.session['credentials'] = {}
#   if not 'myChannelId' in request.session['credentials']:
#     request.session['credentials']['myChannelId'] = channel.channel_id
#   return HttpResponse('Done.'.encode('utf-8'))

@csrf_exempt
def api(request):
  if request.method == 'GET':
    api_response = {
      'message': 'It works!'
    }
  elif request.method == 'POST':
    # Read the request data
    request_data = json.loads(request.body.decode('utf-8'))
    api_response = {
      'message': f'User tried to do action {request_data["action"]}'
    }
  return HttpResponse(json.dumps(api_response), content_type='application/json')

@csrf_exempt
def getUserInfo(request):
  try:
    channel = getChannelFromRequest(request)
    return HttpResponse(json.dumps({
      'name': channel.title,
      'desc': channel.description,
      'channel_id': channel.channel_id
    }), content_type='application/json')
  except:
    return HttpResponse('Not logged in', status=401)
    # Redirect to login

# -------------- CHART RELATED STUFF BELOW -------------

@csrf_exempt
def overviewChart(request):
  myData = []
  myChannel = getChannelFromRequest(request)
  collections = RuleCollection.objects.filter(owner = myChannel)
  myColors = getColors(len(collections))

  for collection in collections:
    rules = Rule.objects.filter(rule_collection = collection)
    matched_comments_ids = set()
    all_matched_comments = []
    for rule in rules:
      for c in getMatchedCommentsForCharts(unifiedRule(rule), myChannel):
        if (c['id'] not in matched_comments_ids):
          all_matched_comments.append(c)
          matched_comments_ids.add(c['id'])
    collectionDict = {
      'label': collection.name,
      'data': ruleDateCounter(all_matched_comments),
      'num_matched_comments': len(all_matched_comments),
      'fill': False,
      'lineTension': 0,
    }
    myData.append(collectionDict)

  myData = nlargest(NUM_CHART_ENTRIES, myData, key=lambda item: item["num_matched_comments"])

  colorCounter = 0
  for collectionDict in myData:
    collectionDict['borderColor'] = myColors[colorCounter]
    collectionDict['backgroundColor'] = myColors[colorCounter]
    colorCounter += 1


  chartConfig = {}
  chartConfig['type'] = 'line'
  chartConfig['data'] = myData
  chartConfig['label'] = 'Number of Comments Caught'
  myColors = getColors(len(myData))
  chartConfig['bgColor'] = myColors
  chartConfig['borderColor'] = myColors

  return HttpResponse(json.dumps(chartConfig), content_type='application/json')


@csrf_exempt
def filterChart(request, filter_id):

  myChannel = getChannelFromRequest(request)
  collections = RuleCollection.objects.filter(owner = myChannel, id=filter_id)
  collection = collections[0]

  rules = Rule.objects.filter(rule_collection = collection)
  myColors = getColors(len(rules))

  myData = []
  for rule in rules:
    rule_matched_comments = getMatchedCommentsForCharts(unifiedRule(rule), myChannel)
    ruleDict = {
      'label': rule.phrase,
      'fill': False,
      'lineTension': 0,
      'num_matched_comments': len(rule_matched_comments),
      'data': ruleDateCounter(rule_matched_comments)
    }
    myData.append(ruleDict)

  myData = nlargest(NUM_CHART_ENTRIES, myData, key=lambda item: item["num_matched_comments"])
  ruleCounter = 0
  for ruleDict in myData:
    ruleDict['borderColor'] = myColors[ruleCounter]
    ruleDict['backgroundColor'] = myColors[ruleCounter]
    ruleCounter += 1


  chartConfig = {}
  chartConfig['type'] = 'line'
  chartConfig['data'] = myData
  chartConfig['label'] = 'Number of Comments Caught'
  myColors = getColors(len(myData))
  chartConfig['bgColor'] = myColors
  chartConfig['borderColor'] = myColors

  return HttpResponse(json.dumps(chartConfig), content_type='application/json')

@csrf_exempt
def ruleChart(request, filter_id, rule_id):
  # make a real chart config based on the one above
  chartConfig = createChartConfig()
  return HttpResponse(json.dumps(chartConfig), content_type='application/json')

# -------------- RULE RELATED STUFF BELOW --------------
@csrf_exempt
def previewRule(request):
  myChannel = getChannelFromRequest(request)
  payload = json.loads(request.body.decode('utf-8'))
  # context is the filter group id
  context, rule = payload['id'], payload['rule']
  matched_comments = getMatchedCommentsAndPrettify(unifiedRule(rule), myChannel)
  num_new_matches = 0
  for comment in matched_comments:
    if (comment['catching_collection'] is None):
      num_new_matches += 1
  response = {
    'comments': matched_comments[:15],
    'num_new_matches': num_new_matches,
  }
  return HttpResponse(json.dumps(response), content_type='application/json')

@csrf_exempt
def getComment(request, comment_id):
  myChannel = getChannelFromRequest(request)
  # TODO: Fix this!
  response = {

  }
  return HttpResponse(json.dumps(response), content_type='application/json')

@csrf_exempt
def previewFilter(request, filter_id):
  myChannel = getChannelFromRequest(request)
  collections = RuleCollection.objects.filter(id = filter_id)
  if (collections):
    collection = collections[0]
    matched_comments = []
    rules = Rule.objects.filter(rule_collection = collection)
    for rule in rules:
      matched_comments += getMatchedCommentsAndPrettify(unifiedRule(rule), myChannel)
    response = {
      'comments': matched_comments,
    }
    return HttpResponse(json.dumps(response), content_type='application/json')
  return HttpResponse('Filter not found'.encode('utf-8'), status = 404)

@csrf_exempt
def loadFilters(request):
  myChannel = getChannelFromRequest(request)
  collections = RuleCollection.objects.filter(owner = myChannel)
  filters = []
  for collection in collections:
    collectionObject = serializeCollection(collection)
    filters.append(collectionObject)

  response = {
    'filters': filters
  }
  return HttpResponse(json.dumps(response), content_type='application/json')

@csrf_exempt
def loadFilter(request, filter_id):
  collections = RuleCollection.objects.filter(id = filter_id)
  if (collections):
    collection = collections[0]
    collectionObject = serializeCollection(collection)
    return HttpResponse(json.dumps(collectionObject), content_type='application/json')
  else:
    return HttpResponse('Filter not found'.encode('utf-8'), status=404)

@csrf_exempt
def createFilter(request):
  myChannel = getChannelFromRequest(request)

  request_data = json.loads(request.body.decode('utf-8'))
  name = request_data['name']
  reference = request_data['reference']

  collection = None
  if reference == 'empty':
    collection = RuleCollection.objects.create(
      name = name,
      create_date = datetime.now(),
      owner = myChannel)
  elif reference.startswith('existing:'):
    collection = RuleCollection.objects.create(
      name = name,
      create_date = datetime.now(),
      owner = myChannel)
    referenceCollection = RuleCollection.objects.get(id = reference[9:])
    for rule in Rule.objects.filter(rule_collection = referenceCollection):
      newRule = Rule.objects.create(
        phrase = rule.phrase,
        exception_phrase = rule.exception_phrase,
        rule_collection = collection,
        case_sensitive = rule.case_sensitive,
        spell_variants = rule.spell_variants,
        )
  elif reference.startswith('template:'):
    collection = RuleCollection.objects.create(
      name = name,
      create_date = datetime.now(),
      owner = myChannel)
    referenceCollection = RuleColTemplate.objects.get(id = reference[9:])
    for rule in Rule.objects.filter(rule_collection = referenceCollection):
      newRule = Rule.objects.create(
        phrase = rule.phrase,
        exception_phrase = rule.exception_phrase,
        rule_collection = collection,
        case_sensitive = rule.case_sensitive,
        spell_variants = rule.spell_variants,
        )
  else:
    return HttpResponse('Unrecognized reference'.encode('utf-8'), status = 400)

  if collection is None:
    return HttpResponse('Creation of filter failed'.encode('utf-8'), status = 500)
  else:
    return HttpResponse(json.dumps(serializeCollection(collection)),
      content_type='application/json')

@csrf_exempt
def updateRule(request):
  myChannel = getChannelFromRequest(request)
  request_data = json.loads(request.body.decode('utf-8'))
  rule = Rule.objects.get(id=int(request_data['id']))

  updateAction = request_data['updateAction']

  if (updateAction == 'toggle_case_sensitive'):
    if (rule.case_sensitive == True):
      rule.case_sensitive = False
    else:
      rule.case_sensitive = True
    rule.save()
    return HttpResponse(json.dumps({
      'id': str(rule.id),
      'case_sensitive': rule.case_sensitive,
    }), content_type='application/json')
  elif (updateAction == 'toggle_spell_variants'):
    if (rule.spell_variants == True):
      rule.spell_variants = False
    else:
      rule.spell_variants = True
    rule.save()
    return HttpResponse(json.dumps({
      'id': str(rule.id),
      'spell_variants': rule.spell_variants,
    }), content_type='application/json')
  else:
    return HttpResponse('Unsupported action'.encode('utf-8'), status = 400)

@csrf_exempt
def updateFilter(request):
  myChannel = getChannelFromRequest(request)

  request_data = json.loads(request.body.decode('utf-8'))
  collection = RuleCollection.objects.get(id=request_data['id'])

  updateAction = request_data['updateAction']
  updateValue = request_data['updateValue']

  if (updateAction == 'name'):
    collection.name = updateValue
    collection.save()
    return HttpResponse(json.dumps({}), content_type='application/json')
  elif (updateAction == 'rules:add'):
    phrase = updateValue['phrase']
    rule = Rule.objects.create(
      phrase = phrase,
      rule_collection = collection,
    )
    return HttpResponse(json.dumps(
      serializeRule(rule)
    ), content_type='application/json')
  elif (updateAction == 'rules:remove'):
    if 'id' in updateValue:
      id = int(updateValue['id'])
      rules = Rule.objects.filter(id = id)
    else:
      return HttpResponse('Rule id not supplied'.encode('utf-8'), status = 400)
    if (rules):
      rule = rules[0]
      rule.delete()
      return HttpResponse(json.dumps({}), content_type='application/json')
    else:
      return HttpResponse('Rule does not exist'.encode('utf-8'), status = 404)
  else:
    return HttpResponse('Unsupported action'.encode('utf-8'), status = 400)

@csrf_exempt
def deleteFilter(request):
  request_data = json.loads(request.body.decode('utf-8'))
  collections = RuleCollection.objects.filter(id = request_data['id'])
  if (collections):
    collection = collections[0]
    collection.delete()
    return HttpResponse(json.dumps({}), content_type='application/json')
  else:
    return HttpResponse('Collection does not exist'.encode('utf-8'), status = 404)

def random_date():
  """Generate a random datetime between `start` and `end`"""
  end = datetime(2021, 8, 19, 1, 0, 0)
  start = end - timedelta(days=90)
  return start + timedelta(
    # Get a random amount of seconds between `start` and `end`
    seconds=random.randint(0, int((end - start).total_seconds())),
  )

def random_string():
  return ''.join(random.choices(string.ascii_uppercase + string.digits, k=15))

def randomizeComment(comment_text):
  replacements = ['ass whore', 'faggot', 'ass man', 'bulldyke', 'buttfuck', 'carpet muncher', 'cocksucker', 'dyke', 'fag', 'fingerfucker']
  replacements += ['fudgepacker', 'gayass', 'muffindiver', 'pussyeater', 'sodomite', 'lezbo']
  replacements += ['annihilate', 'bang', 'choke', 'batter', 'brutalise', 'butcher', 'clobber', 'decimate', 'flagellate', 'punch', 'strangle', 'trample', 'whip']
  replacements += ['pound', 'gangbang', 'incest', 'molest']
  replacements += ['whore', 'bitch', 'cunt', 'slut', 'twat']
  replacements += ['butt', 'blowjob', 'deepthroat', 'femdom', 'octopussy', 'schlong']

  anchor = None
  if ('the' in comment_text):
    anchor = 'the'
  elif ('that' in comment_text):
    anchor = 'that'
  elif ('with' in comment_text):
    anchor = 'with'
  elif ('from' in comment_text):
    anchor = 'from'
  else:
    return comment_text
  if (random.randrange(100) < 30):
    replacement = random.sample(replacements, 1)[0]
    new_str = comment_text.replace(anchor, replacement)
    return new_str
  else:
    return comment_text

def createTestVideos(myChannel):
  titles = [
    'Trump slams Biden over Afghanistan & Inflation',
    'Disgruntled Trump Actively Undermines Vaccination Push',
    'Goodbye Donald Trump',
    'Donald Trump vows to ban Muslims Entering US',
    'Red Pill: A search for dating advice turns into radicalization',
  ]

  videos = []

  for title in titles:
    updated_values = {
      'pub_date': random_date(),
      'video_id': random_string(),
      'channel': myChannel,
    }
    video, created = Video.objects.update_or_create(title = title, defaults=updated_values)
    videos.append(video)
  return videos

def createTestEntries(request):
  import pandas as pd
  myChannel = getChannelFromRequest(request)

  csv_path = os.path.join(os.path.dirname(__file__), 'sample_entries.csv')
  df = pd.read_csv(csv_path)
  videos = createTestVideos(myChannel)
  for index, row in df.iterrows():
    if (index < 800):
      video = random.sample(videos[:4], 1)[0]
    else:
      video = videos[4]
    updated_values = {
      'pub_date': random_date(),
      'video': video,
      'parent_id': '',
      'text': randomizeComment(row['text']),
    }
    comment, created = Comment.objects.update_or_create(
      author = row['author'],
      likeCount = int(row['likeCount']),
      comment_id = row['comment_id'],
      defaults=updated_values
      )
  return HttpResponseRedirect('/overview')
