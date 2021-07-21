# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.views.generic import TemplateView
from django.http import HttpResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt

from .util_rules import getMatchedComments, serializeComment
from .util_filters import serializeRules, serializeCollection
from .models import Channel, RuleCollection, Rule, Video, Comment, Reply

from datetime import datetime
import urllib.request, json

def makeDebugChannel():
  try:
    return Channel.objects.get(channel_id = '')
  except:
    return Channel.objects.create(
      title='Debug channel',
      channel_id='',
      description='',
      pub_date=datetime.now()
    )

def getChannel(request):
  if 'credentials' in request.session and 'myChannelId' in request.session['credentials']:
    myChannelId = request.session['credentials']['myChannelId']
    myChannel = Channel.objects.get(channel_id = myChannelId)
    return myChannel
  else:
    return makeDebugChannel()
    #raise Exception('Could not get login gredentials')

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
  return HttpResponse(json.dumps(api_response), content_type='text/json')

@csrf_exempt
def previewRule(request, rule_id):
  myChannel = getChannel(request)
  rules = Rule.objects.filter(id=rule_id)
  if (rules):
    rule = rules[0]
    matched_comments = getMatchedComments(rule, myChannel)
    response = {
    	'matched_comments': matched_comments,
    }
  else:
  	response = {
  		'matched_comments': None,
  	}
  return HttpResponse(json.dumps(response), content_type='application/json')

@csrf_exempt
def getComment(request, comment_id):
	myComment = Comment.objects.filter(id = comment_id)
	if (myComment):
		commentObject = serializeComment(myComment)
		response = {
			'comment': commentObject
		}
	else:
		response = {
			'comment': None
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
			matched_comments += getMatchedComments(rule, myChannel)
		response = {
			'matched_comments': matched_comments,
	  }
	else:
		response = {
	    'matched_comments': None,
	  }
	return HttpResponse(json.dumps(response), content_type='application/json')

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
    return HttpResponse(json.dumps({
        'id': collection.id
      }), content_type='application/json')

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
    rule = Rule.objects.create(
      phrase = updateValue,
      rule_collection = collection,
    )
    return HttpResponse(json.dumps({}), content_type='application/json')
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
