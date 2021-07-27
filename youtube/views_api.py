# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.views.generic import TemplateView
from django.http import HttpResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt

from .util_rules import getMatchedComments, serializeComment, serializeCommentWithPhrase, getColors
from .util_filters import serializeRules, serializeCollection
from .models import Channel, RuleCollection, Rule, Video, Comment, Reply

from datetime import datetime
import urllib.request, json
import random
from collections import defaultdict

def makeDebugChannel(channel_id = ''):
  try:
    return Channel.objects.get(channel_id = channel_id)
  except:
    return Channel.objects.create(
      title='Debug channel',
      channel_id=channel_id,
      description='This is a temporary debugging channel',
      pub_date=datetime.now())

def getChannel(request):
  if 'credentials' in request.session and 'myChannelId' in request.session['credentials']:
    myChannelId = request.session['credentials']['myChannelId']
    myChannel = Channel.objects.get(channel_id = myChannelId)
    return myChannel
  else:
    #return makeDebugChannel()
    raise Exception('Could not get login gredentials')

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

@csrf_exempt
def debug(request):
  channel_id = ''
  try:
    request_data = json.loads(request.body.decode('utf-8'))
    channel_id = request_data['channel']
  except:
    pass
  channel = makeDebugChannel(channel_id = channel_id)
  if not 'credentials' in request.session:
    request.session['credentials'] = {}
  if not 'myChannelId' in request.session['credentials']:
    request.session['credentials']['myChannelId'] = channel.channel_id
  return HttpResponse('Done.'.encode('utf-8'))

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
    channel = getChannel(request)
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
  myData = {}
  myChannel = getChannel(request)
  collections = RuleCollection.objects.filter(owner = myChannel)
  for collection in collections:
    rules = Rule.objects.filter(rule_collection = collection)
    matched_comments = set()
    for rule in rules:
      for c in getMatchedComments(unifiedRule(rule), myChannel):
        matched_comments.add(c['id'])
    myData[collection.name] = len(matched_comments)

  chartConfig = {}
  chartConfig['type'] = 'bar'
  chartConfig['data'] = myData
  chartConfig['label'] = 'Number of Comments Caught'
  # myColors = random.choices(range(256), k=len(myData))
  myColors = getColors(len(myData))
  chartConfig['bgColor'] = myColors
  chartConfig['borderColor'] = myColors

  return HttpResponse(json.dumps(chartConfig), content_type='application/json')

def convertDate(myDate):
  newDate = datetime.strptime(myDate, '%m/%d/%Y, %H:%M:%S').strftime('%Y/%m/%d')  
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


@csrf_exempt
def filterChart(request, filter_id):
  
  myChannel = getChannel(request)
  collections = RuleCollection.objects.filter(owner = myChannel, id=filter_id)
  collection = collections[0]

  rules = Rule.objects.filter(rule_collection = collection)
  myColors = getColors(len(rules))

  ruleCounter = 0
  myData = []
  for rule in rules:
    ruleDict = {
      'label': rule.phrase,
      'borderColor': myColors[ruleCounter],
    }
    rule_matched_comments = getMatchedComments(unifiedRule(rule), myChannel)
    ruleDict['data'] = ruleDateCounter(rule_matched_comments)
    myData.append(ruleDict)
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
  myChannel = getChannel(request)
  payload = json.loads(request.body.decode('utf-8'))
  # context is the filter group id
  context, rule = payload['id'], payload['rule']
  response = {
    'comments': getMatchedComments(unifiedRule(rule), myChannel)
  }
  return HttpResponse(json.dumps(response), content_type='application/json')

@csrf_exempt
def getComment(request, comment_id):
  myChannel = getChannel(request)
  # TODO: Fix this!
  response = {

  }
  return HttpResponse(json.dumps(response), content_type='application/json')

@csrf_exempt
def previewFilter(request, filter_id):
  myChannel = getChannel(request)
  collections = RuleCollection.objects.filter(id = filter_id)
  if (collections):
    collection = collections[0]
    matched_comments = []
    rules = Rule.objects.filter(rule_collection = collection)
    for rule in rules:
      matched_comments += getMatchedComments(unifiedRule(rule), myChannel)
    response = {
      'comments': matched_comments
    }
    return HttpResponse(json.dumps(response), content_type='application/json')
  return HttpResponse('Filter not found'.encode('utf-8'), status = 404)

@csrf_exempt
def loadFilters(request):
  myChannel = getChannel(request)
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
  myChannel = getChannel(request)

  request_data = json.loads(request.body.decode('utf-8'))
  name = request_data['name']
  reference = request_data['reference']

  collection = None
  if reference == 'empty':
    collection = RuleCollection.objects.create(
      name = name,
      create_date = datetime.now(),
      owner = myChannel,
      is_template = False)
  elif reference.startswith('existing:'):
    collection = RuleCollection.objects.create(
      name = name,
      create_date = datetime.now(),
      owner = myChannel,
      is_template = False)
    referenceCollection = RuleCollection.objects.get(id = reference[9:])
    for rule in Rule.objects.filter(rule_collection = referenceCollection):
      newRule = Rule.objects.create(
        phrase = rule.phrase,
        exception_phrase = rule.exception_phrase,
        rule_collection = collection)
  elif reference.startswith('template:'):
    pass
  else:
    return HttpResponse('Unrecognized reference'.encode('utf-8'), status = 400)

  if collection is None:
    return HttpResponse('Creation of filter failed'.encode('utf-8'), status = 500)
  else:
    return HttpResponse(json.dumps(serializeCollection(collection)),
      content_type='application/json')

@csrf_exempt
def updateFilter(request):
  myChannel = getChannel(request)

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
    return HttpResponse(json.dumps({
      'id': rule.id
    }), content_type='application/json')
  elif (updateAction == 'rules:remove'):
    rules = Rule.objects.filter(id = updateValue)
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
