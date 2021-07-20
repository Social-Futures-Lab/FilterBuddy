# -*- coding: utf-8 -*-

from django.shortcuts import render
from django.views.generic import TemplateView
from django.http import HttpResponse, HttpResponseRedirect

from django.views.decorators.csrf import csrf_exempt
from .models import Channel, RuleCollection, Rule, Video, Comment, Reply

from datetime import datetime
import urllib.request, json


def serializeRules(collection):
    rules = Rule.objects.filter(rule_collection = collection)
    rulesList = []
    for rule in rules:
        rulesList.append(
            {
                'phrase': rule.phrase,
                'exception_phrase': rule.exception_phrase,
            }
            )
    return rulesList

def serializeCollection(collection):
    collectionObject = {
        'title': collection.title,
        'pub_date': collection.pub_date,
        'rules': serializeRules(collection),
        }
    return collectionObject


def loadFilters(request):
    myChannelId = request.session['credentials']['myChannelId']
    myChannel = Channel.objects.get(channel_id = myChannelId)
    collections = RuleCollection.objects.filter(channel = myChannel)
    filters = []
    for collection in collections:
        collectionObject = serializeCollection(collection)
        filters.append(collectionObject)

    response = {
        'filters': filters
    }    
    return HttpResponse(json.dumps(response), content_type='application/json')

def loadFilter(request, filter_id):
    collections = RuleCollection.objects.filter(id = filter_id)
    if (collections):
        collection = collections[0]
        collectionObject = serializeCollection(collection)
        response = {
            'filter': collectionObject
        }    
    else:
        response = {
        'filter': None
        }
    return HttpResponse(json.dumps(response), content_type='application/json')    

def createFilter(request):
    myChannelId = request.session['credentials']['myChannelId']
    myChannel = Channel.objects.get(channel_id = myChannelId)

    request_data = json.loads(request.body.decode('utf-8'))
    name = request_data['name']
    reference = request_data['reference']
    collection = RuleCollection.objects.create(
            title = name,
            pub_date = datetime.now(),
            channel = myChannel,
            is_template = False,
            )    
    if (reference and 'existing' in reference.keys()):
        referenceCollection = RuleCollection.objects.get(id=reference['existing'])
        for rule in Rule.objects.filter(rule_collection = referenceCollection):
            newRule = Rule.objects.create(
                phrase = rule.phrase,
                exception_phrase = rule.exception_phrase,
                rule_collection = collection,
                )

    response = {
    'id': collection.id,
    }
    return HttpResponse(json.dumps(response), content_type='application/json')        

def updateFilter(request):
    myChannelId = request.session['credentials']['myChannelId']
    myChannel = Channel.objects.get(channel_id = myChannelId)

    request_data = json.loads(request.body.decode('utf-8'))
    collection = RuleCollection.objects.get(id=request_data['id'])

    updateAction = request_data['updateAction']
    updateValue = request_data['updateValue']
    if (updateAction == 'name'):
        collection.title = updateValue
        collection.save()
        message = "Collection name is updated."

    elif (updateAction == 'rules:add'):
        rule = Rule.objects.create(
            phrase = updateValue,
            rule_collection = collection,
            )
        message = "New rules has been added"
    
    elif (updateAction == 'rules:remove'):
        rules = Rule.objects.filter(id=updateValue)
        if (rules):
            rule = rules[0]
            rule.delete()
            message = "Rule has been deleted."
        else:
            message = "Rule not found."

    reponse = {
    'message': message,
    }

    return HttpResponse(json.dumps(response), content_type='application/json')            



    

def deleteFilter(request, filter_id):
    collections = RuleCollection.objects.filter(id = filter_id)
    if (collections):
        collection = collections[0]
        collection.delete()
        reponse = {
        'message': 'Rule collection has been deleted.'
        }    
    else:
        reponse = {
        'message': 'Rule collection not found.'
        }           
    return HttpResponse(json.dumps(response), content_type='application/json')            




