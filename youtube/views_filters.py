# -*- coding: utf-8 -*-

from django.shortcuts import render
from django.views.generic import TemplateView
from django.http import HttpResponse, HttpResponseRedirect

from django.views.decorators.csrf import csrf_exempt
from .models import Channel, RuleCollection, Rule, Video, Comment, Reply


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

def createFilter(request, name, reference):
    myChannelId = request.session['credentials']['myChannelId']
    myChannel = Channel.objects.get(channel_id = myChannelId)
    

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




