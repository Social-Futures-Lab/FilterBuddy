# -*- coding: utf-8 -*-

from django.shortcuts import render
from django.views.generic import TemplateView
from django.http import HttpResponse, HttpResponseRedirect

from django.views.decorators.csrf import csrf_exempt
from .models import Channel, RuleCollection, Rule, Video, Comment, Reply
from .utils import *

import re

def serializeComment(myComment, phrase):
	k = re.search(r'\b({})\b'.format(phrase), myComment.text)
	commentObject = {
	'id': myComment.id,
	'text': myComment.text,
	'author': myComment.author,
	'likeCount': myComment.likeCount,
	'pub_date': myComment.pub_date.strftime("%m/%d/%Y, %H:%M:%S"),
	'span': k.span()
	}
	return commentObject

def serializeComment(myComment):
	commentObject = {
	'id': myComment.id,
	'text': myComment.text,
	'author': myComment.author,
	'likeCount': myComment.likeCount,
	'pub_date': myComment.pub_date.strftime("%m/%d/%Y, %H:%M:%S"),
	}
	return commentObject	

def getMatchedComments(rule):
	phrase = rule.phrase
	myComments = Comment.objects.filter(video__channel = myChannel) 
    matched_comments = []
    for myComment in myComments:
        if (phrase in myComment.text):
        	matched_comment = serializeComment(myComment, phrase)
        	matched_comments.append(matched_comment)
        replies = Reply.objects.filter(comment = myComment)
        for reply in replies:
            if (phrase in reply.text):
            	matched_comment = serializeComment(reply, phrase)
            	matched_comments.append(matched_comment)	
    return matched_comments


def previewRule(request, rule_id):
    myChannelId = request.session['credentials']['myChannelId']
    myChannel = Channel.objects.get(channel_id = myChannelId)	
	rules = Rule.objects.filter(id = rule_id)
	if (rules):
		rule = rules[0]
		matched_comments = getMatchedComments(rule)
	    response = {
	            'matched_comments': matched_comments,
	        }    
	 else:
	 	response = {
	            'matched_comments': None,
	        }    
    return HttpResponse(json.dumps(response), content_type='application/json')        		

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

def previewFilter(request, filter_id):
	collections = RuleCollection.objects.filter(id = filter_id)
	if (collections):
		collection = collections[0]
		matched_comments = []
		rules = Rule.objects.filter(rule_collection = collection)
		for rule in rules:
			matched_comments.append(getMatchedComments(rule))
	    response = {
	            'matched_comments': matched_comments,
	        }    			
	else:
		response = {
	            'matched_comments': None,
	        }    
    return HttpResponse(json.dumps(response), content_type='application/json')        		
