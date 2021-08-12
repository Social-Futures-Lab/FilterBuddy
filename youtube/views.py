# -*- coding: utf-8 -*-

import os
import requests
import sys

import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery

from django.shortcuts import render
from django.views.generic import TemplateView
from django.http import HttpResponse, HttpResponseRedirect

from django import forms
from django.views.generic.edit import FormView
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.urls import reverse
from django.conf import settings

import dateutil.parser
import datetime
import urllib.request, json
import re
import copy

from .models import Channel, RuleCollection, RuleColTemplate, Rule, Video, Comment
from .utils import *
from .util_rules import getChannel as getChannelFromRequest

class YouTubeForm(forms.Form):
  pass

class HomePageView(FormView):
  template_name = 'youtube/home.html'
  form_class = YouTubeForm

# Create your views here.
def index(request):
  return render(request, "youtube/home.html")

def getChannel(credentials):
  youtube = googleapiclient.discovery.build(
    API_SERVICE_NAME, API_VERSION, credentials=credentials)

  channels = youtube.channels().list(mine=True, part='snippet').execute()
  if not 'items' in channels:
    return None
  for channel in channels['items']:
    channel['snippet']['publishedAt'] = dateutil.parser.parse(channel['snippet']['publishedAt'])
  myChannel = channels['items'][0]

  djangoChannel, created = Channel.objects.get_or_create(
    title=myChannel['snippet']['title'],
    description=myChannel['snippet']['description'],
    pub_date=myChannel['snippet']['publishedAt'],
    channel_id=myChannel['id'])
  return djangoChannel

def about_us(request):
  return render(request, 'youtube/about_us.html')

def mytest(request):
  return render(request, 'youtube/mytest.html', {})


def test_api_request(request):
  if 'credentials' not in request.session:
    return authorize(request)

  # Load credentials from the session.
  sc = request.session['credentials']
  credentials = google.oauth2.credentials.Credentials(
    token = sc.get('token'),
    refresh_token = sc.get('refresh_token'),
    token_uri = sc.get('token_uri'),
    client_id = sc.get('client_id'),
    client_secret = sc.get('client_secret'),
    scopes = sc.get('scopes')
  )

  channel = getChannel(credentials)

  # Save credentials back to session in case access token was refreshed.
  # ACTION ITEM: In a production app, you likely want to save these
  #        credentials in a persistent database instead.
  request.session['credentials'] = credentials_to_dict(credentials)
  request.session['credentials']['myChannelId'] = channel.channel_id
  channelDict = {
    'title': channel.title,
    'description': channel.description,
    'publishedAt': channel.pub_date,
    'id': channel.channel_id}
  return render(request, 'youtube/profile.html', {'channel': channelDict,})
  # return JsonResponse(channel)


def authorize(request):
  flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
    CLIENT_SECRETS_FILE, scopes=SCOPES)
  # The URI created here must exactly match one of the authorized redirect URIs
  # for the OAuth 2.0 client, which you configured in the API Console. If this
  # value doesn't match an authorized URI, you will get a 'redirect_uri_mismatch'
  # error.

  # flow.redirect_uri = reverse('youtube:oauth2callback')
  flow.redirect_uri = "https://wordfilters.railgun.in/oauth2callback"

  authorization_url, state = flow.authorization_url(
    # Enable offline access so that you can refresh an access token without
    # re-prompting the user for permission. Recommended for web server apps.
    access_type='offline',
    # Enable incremental authorization. Recommended as a best practice.
    include_granted_scopes='true')

  # Store the state so the callback can verify the auth server response.
  request.session['state'] = state
  return HttpResponseRedirect(authorization_url)


def oauth2callback(request):
  # Specify the state when creating the flow in the callback so that it can
  # verified in the authorization server response.
  state = request.session['state']

  flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
    CLIENT_SECRETS_FILE, scopes=SCOPES, state=state)
  # flow.redirect_uri = reverse('youtube:oauth2callback')
  flow.redirect_uri = 'https://wordfilters.railgun.in/oauth2callback'

  # Use the authorization server's response to fetch the OAuth 2.0 tokens.
  authorization_response = request.build_absolute_uri().replace('http', 'https')
  flow.fetch_token(authorization_response=authorization_response)

  # Store credentials in the session.
  # ACTION ITEM: In a production app, you likely want to save these
  #        credentials in a persistent database instead.
  credentials = flow.credentials
  request.session['credentials'] = credentials_to_dict(credentials)

  channel = getChannel(credentials)
  if channel is None:
    raise Exception('This account has no channels')

  # Save credentials back to session in case access token was refreshed.
  # ACTION ITEM: In a production app, you likely want to save these
  #        credentials in a persistent database instead.
  request.session['credentials']['myChannelId'] = channel.channel_id
  channelDict = {
    'title': channel.title,
    'description': channel.description,
    'publishedAt': channel.pub_date,
    'id': channel.channel_id}
  return HttpResponseRedirect(reverse('youtube:home'))

def revoke(request):
  if 'credentials' not in request.session:
    return HttpResponse('You need to <a href="/authorize">authorize</a> before ' +
      'testing the code to revoke credentials.')

  # Load credentials from the session.
  sc = request.session['credentials']
  credentials = google.oauth2.credentials.Credentials(
    token = sc.get('token'),
    refresh_token = sc.get('refresh_token'),
    token_uri = sc.get('token_uri'),
    client_id = sc.get('client_id'),
    client_secret = sc.get('client_secret'),
    scopes = sc.get('scopes')
  )
  revoke = requests.post('https://oauth2.googleapis.com/revoke',
    params={'token': credentials.token},
    headers = {'content-type': 'application/x-www-form-urlencoded'})
  status_code = getattr(revoke, 'status_code')
  if status_code == 200:
    page_message = 'Credentials successfully revoked.'
  else:
    page_message = 'An error occurred.'
  return render(request, "youtube/home.html", {'page_message': page_message})


def clear_credentials(request):
  if 'credentials' in request.session:
    del request.session['credentials']
  page_message = 'Credentials have been cleared.'
  # return render(request, "youtube/home.html", {'page_message': page_message})
  return HttpResponseRedirect(reverse('youtube:authorize'))

@csrf_exempt
def get_videos(request):
  if 'credentials' not in request.session:
    return authorize(request)

  # Load credentials from the session.
  sc = request.session['credentials']
  if 'myChannelId' not in sc:
    credentials = google.oauth2.credentials.Credentials(
      token = sc.get('token'),
      refresh_token = sc.get('refresh_token'),
      token_uri = sc.get('token_uri'),
      client_id = sc.get('client_id'),
      client_secret = sc.get('client_secret'),
      scopes = sc.get('scopes')
    )
    myChannel = getChannel(credentials)
    sc['myChannelId'] = myChannel.channel_id
  else:
    myChannelId = sc['myChannelId']
    myChannel = Channel.objects.get(channel_id = myChannelId)
  myChannelId = myChannel.channel_id

  videoFetchUrl = "https://www.googleapis.com/youtube/v3/search?order=date&part=snippet&type=video&channelId=%s&maxResults=1000&key=%s" % (myChannelId, DEVELOPER_KEY,)

  videos = []
  with urllib.request.urlopen(videoFetchUrl) as url:
    data = json.loads(url.read().decode())
    for item in data['items']:
      publishedAt = item['snippet']['publishedAt']
      title = item['snippet']['title']
      videoId = item['id']['videoId']
      pub_date = dateutil.parser.parse(publishedAt)
      videos.append({
        'videoId': videoId,
        'title': title,
        'publishTime': publishedAt
      })
      video, created = Video.objects.get_or_create(title = title, pub_date = pub_date, video_id = videoId, channel = myChannel)
  response = {
    'video': videos
  }
  return HttpResponse(json.dumps(response), content_type='application/json')
  #return render(request, 'youtube/videos.html', {'videos': videos})


def get_comments(request):
  if 'credentials' not in request.session:
    return authorize(request)

  # Load credentials from the session.
  sc = request.session['credentials']
  if 'myChannelId' not in sc:
    credentials = google.oauth2.credentials.Credentials(
      token = sc.get('token'),
      refresh_token = sc.get('refresh_token'),
      token_uri = sc.get('token_uri'),
      client_id = sc.get('client_id'),
      client_secret = sc.get('client_secret'),
      scopes = sc.get('scopes')
    )
    myChannel = getChannel(credentials)
    sc['myChannelId'] = myChannel.channel_id
  else:
    myChannelId = sc['myChannelId']
    myChannel = Channel.objects.get(channel_id = myChannelId)
  myChannelId = myChannel.channel_id

  videoFetchUrl = "https://www.googleapis.com/youtube/v3/search?order=date&part=snippet&type=video&channelId=%s&maxResults=1000&key=%s" % (myChannelId, DEVELOPER_KEY,)
  myVideoIds = []
  with urllib.request.urlopen(videoFetchUrl) as url:
    data = json.loads(url.read().decode())
    for item in data['items']:
      if 'videoId' in item['id'].keys():
        myVideoIds.append(item['id']['videoId'])

  youtube = googleapiclient.discovery.build(API_SERVICE_NAME, API_VERSION, developerKey = DEVELOPER_KEY)

  myComments = []
  for video_id in myVideoIds:
    comments = get_comments_from_video(youtube, video_id)
    myComments += comments
  myComments = sorted(myComments, key=lambda k: k.pub_date, reverse=True)
  return render(request, 'youtube/comments.html', {'comments': myComments})

def get_video_comments(request, video_id):
  youtube = googleapiclient.discovery.build(API_SERVICE_NAME, API_VERSION, developerKey = DEVELOPER_KEY)
  comments = get_comments_from_video(youtube, video_id)
  video_url = "https://www.youtube.com/watch?v=%s" % (video_id,)
  return render(request, 'youtube/comments.html', {'comments': comments, 'video_id': video_id, 'video_url': video_url})

def saveCommentObject(youtube, item, video):
  text = item['snippet']['topLevelComment']['snippet']['textDisplay']
  pub_date = dateutil.parser.parse(item['snippet']['topLevelComment']['snippet']['publishedAt'])
  author = item['snippet']['topLevelComment']['snippet']['authorDisplayName']
  likeCount = item['snippet']['topLevelComment']['snippet']['likeCount']
  comment_id = item['snippet']['topLevelComment']['id']
  updated_values = {
    'text': text,
    'pub_date': pub_date,
    'author': author,
    'likeCount': likeCount
  }
  comment, created = Comment.objects.update_or_create(video=video, comment_id=comment_id, defaults=updated_values)
  if (item['snippet']['totalReplyCount'] > 0):
    replies = get_replies(youtube, comment)
  return comment

def get_comments_from_video(youtube, video_id):
  comments = []
  vid_stats = youtube.videos().list(part="statistics", id=video_id).execute()
  comment_count = vid_stats.get("items")[0].get("statistics").get("commentCount")
  video = Video.objects.get(video_id=video_id)

  if (comment_count and int(comment_count)>0):
    video_response = youtube.commentThreads().list(part="snippet", videoId=video_id, textFormat="plainText").execute()
    # Get the first set of comments
    for item in video_response['items']:
      comment = saveCommentObject(youtube, item, video)
      comments.append(comment)

    # Keep getting comments from the following pages
    while ("nextPageToken" in video_response):
      video_response = youtube.commentThreads().list(part="snippet", videoId=video_id, pageToken=video_response["nextPageToken"], textFormat="plainText").execute()
      for item in video_response['items']:
        comment = saveCommentObject(youtube, item, video)
        comments.append(comment)
  return comments

def get_replies(youtube, parent):
  results = youtube.comments().list(part="snippet", parentId=parent.comment_id, textFormat="plainText").execute()
  replies = []
  for item in results['items']:
    text = item['snippet']['textDisplay']
    pub_date = dateutil.parser.parse(item['snippet']['publishedAt'])
    author = item['snippet']['authorDisplayName']
    likeCount = item['snippet']['likeCount']
    reply_id = item['id']
    updated_values = {
      'text': text,
      'pub_date': pub_date,
      'author': author,
      'likeCount': likeCount
    }
    reply, created = Comment.objects.update_or_create(video=parent.video, comment_id=reply_id, parent_id=parent.comment_id, defaults=updated_values)
    replies.append(reply)
  return replies

def credentials_to_dict(credentials):
  return {'token': credentials.token,
      'refresh_token': credentials.refresh_token,
      'token_uri': credentials.token_uri,
      'client_id': credentials.client_id,
      'client_secret': credentials.client_secret,
      'scopes': credentials.scopes}

def home(request):
  return render(request, "youtube/create_word_filter.html")

def overview(request):
  myChannel = getChannelFromRequest(request)
  collections = RuleCollection.objects.filter(owner = myChannel)
  return render(request,
    "youtube/page_overview.html",
    {
      'collections': collections,
      'current': {
        'page': 'overview',
        'collection': None
      }
    })

def edit_word_filter(request, filter_id):
  myChannel = getChannelFromRequest(request)
  collections = RuleCollection.objects.filter(owner = myChannel)
  current_collection = RuleCollection.objects.get(
    owner = myChannel, id = filter_id)
  if current_collection is None:
    raise Exception('Trying to load nonexistant or foreign collection.')
  return render(request,
    "youtube/page_collection_edit.html",
    {
      'collections': collections,
      'current': {
        'page': 'edit',
        'collection': current_collection
      }
    })

def overview_word_filter(request, filter_id):
  myChannel = getChannelFromRequest(request)
  collections = RuleCollection.objects.filter(owner = myChannel)
  current_collection = RuleCollection.objects.get(
    owner = myChannel, id = filter_id)
  if current_collection is None:
    raise Exception('Trying to load nonexistant or foreign collection.')
  return render(request,
    "youtube/page_collection_overview.html",
    {
      'collections': collections,
      'current': {
        'page': 'edit',
        'collection': current_collection
      }
    })

def create_word_filter(request):
  myChannel = getChannelFromRequest(request)
  collections = RuleCollection.objects.filter(owner = myChannel)
  ruleTemplates =  RuleColTemplate.objects.all()
  return render(request,
    "youtube/page_collection_add.html",
    {
      'collections': collections,
      'current': {
        'page': 'add',
        'collection': None
      },
      'rule_templates': ruleTemplates,
    })

def get_matching_comments(request, phrase):
  if 'credentials' not in request.session:
    return authorize(request)

  print ("phrase is: ", phrase)
# Load credentials from the session.
  sc = request.session['credentials']

  myChannelId = sc['myChannelId']
  myChannel = Channel.objects.get(channel_id = myChannelId)
  myComments = Comment.objects.filter(video__channel = myChannel)
  matched_comments = []
  for myComment in myComments:
    if (phrase in myComment.text):
      matched_comment = {
      'text': myComment.text,
      'author': myComment.author,
      'likeCount': myComment.likeCount,
      'pub_date': myComment.pub_date.strftime("%m/%d/%Y, %H:%M:%S"),
      }
      matched_comments.append(matched_comment)
  response = {
      'matched_comments': matched_comments,
    }
  return HttpResponse(json.dumps(response), content_type='application/json')


def search_reg_exp(reg_exp, comments, highlight_words=False):
  def highlight(match):
    return "<strong>" + match.group() + "</strong>"
  matching_comments = []
  for comment in comments:
    if highlight_words:
      res_and_num_changes = re.subn(reg_exp, highlight, comment.text)
      if res_and_num_changes[1] > 0:
        matched_comment = copy.copy(comment)
        matched_comment.text = res_and_num_changes[0]
        matching_comments.append(matched_comment)
    elif re.search(reg_exp, comment.text) != None:
      matching_comments.append(comment)
  return matching_comments

@csrf_exempt
def get_rule_collection_templates(request):
  ruleTemplates = RuleCollection.objects.filter(is_template=True)
  templates = []
  for ruleTemplate in ruleTemplates:
    rules = []
    for rule in Rule.objects.filter(rule_collection = ruleTemplate):
      rules.append({
        'phrase': rule.phrase,
        'exception': rule.exception_phrase
        })
    template = {
      'title': ruleTemplate.title,
      'rules': rules
    }
    templates.append(template)
  response = {
    'filters': templates
  }
  return HttpResponse(json.dumps(response), content_type='application/json')

@csrf_exempt
def sync(request):
  myChannel = getChannelFromRequest(request)
  myChannelId = myChannel.channel_id
  videoFetchUrl = "https://www.googleapis.com/youtube/v3/search?order=date&part=snippet&type=video&channelId=%s&maxResults=1000&key=%s" % (myChannelId, DEVELOPER_KEY,)
  myVideoIds = []
  with urllib.request.urlopen(videoFetchUrl) as url:
    data = json.loads(url.read().decode())
    for item in data['items']:
      if 'videoId' in item['id'].keys():
        publishedAt = item['snippet']['publishedAt']
        title = item['snippet']['title']
        videoId = item['id']['videoId']
        myVideoIds.append(videoId)
        pub_date = dateutil.parser.parse(publishedAt)
        video, created = Video.objects.get_or_create(title = title, pub_date = pub_date, video_id = videoId, channel = myChannel)

  youtube = googleapiclient.discovery.build(API_SERVICE_NAME, API_VERSION, developerKey = DEVELOPER_KEY)

  for video_id in myVideoIds:
    get_comments_from_video(youtube, video_id)

  return HttpResponse('Done.'.encode('utf-8'))

if __name__ == '__main__':
  # When running locally, disable OAuthlib's HTTPs verification.
  # ACTION ITEM for developers:
  #   When running in production *do not* leave this option enabled.
  os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
