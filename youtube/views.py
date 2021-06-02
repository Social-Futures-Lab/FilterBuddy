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
from django.http import JsonResponse
from django.urls import reverse
from django.conf import settings

import dateutil.parser
import datetime
import urllib.request, json

class YouTubeForm(forms.Form):
    pass


class HomePageView(FormView):
    template_name = 'youtube/home.html'
    form_class = YouTubeForm


# Create your views here.

# This variable specifies the name of a file that contains the OAuth 2.0
# information for this application, including its client_id and client_secret.
CLIENT_SECRETS_FILE = "/home/ubuntu/mysite/youtube/client_secret_youtube.json"
DEVELOPER_KEY_FILE = "/home/ubuntu/mysite/youtube/developer_key.txt"


# This OAuth 2.0 access scope allows for full read/write access to the
# authenticated user's account and requires requests to use an SSL connection.
SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'
DEVELOPER_KEY = open(DEVELOPER_KEY_FILE).read()



def index(request):
    return render(request, "youtube/home.html")


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
    youtube = googleapiclient.discovery.build(
        API_SERVICE_NAME, API_VERSION, credentials=credentials)

    channels = youtube.channels().list(mine=True, part='snippet').execute()
    for channel in channels['items']:
        channel['snippet']['publishedAt'] = dateutil.parser.parse(channel['snippet']['publishedAt'])
    myChannelId = channels["items"][0]["id"]

    # Save credentials back to session in case access token was refreshed.
    # ACTION ITEM: In a production app, you likely want to save these
    #              credentials in a persistent database instead.
    request.session['credentials'] = credentials_to_dict(credentials)
    request.session['credentials']['myChannelId'] = myChannelId
    return render(request, 'youtube/profile.html', channels)
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
    authorization_response = request.build_absolute_uri()
    flow.fetch_token(authorization_response=authorization_response)

    # Store credentials in the session.
    # ACTION ITEM: In a production app, you likely want to save these
    #              credentials in a persistent database instead.
    credentials = flow.credentials
    request.session['credentials'] = credentials_to_dict(credentials)
    print("Goodbye cruel world!", file=sys.stderr)
    return HttpResponseRedirect(reverse('youtube:test'))

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
    return render(request, "youtube/home.html", {'page_message': page_message})

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
        youtube = googleapiclient.discovery.build(
            API_SERVICE_NAME, API_VERSION, credentials=credentials)

        channels = youtube.channels().list(mine=True, part='snippet').execute()
        myChannelId = channels["items"][0]["id"]
        sc['myChannelId'] = myChannelId
    else:
        myChannelId = sc['myChannelId']

    videoFetchUrl = "https://www.googleapis.com/youtube/v3/search?order=date&part=snippet&type=video&channelId=%s&maxResults=1000&key=%s" % (myChannelId, DEVELOPER_KEY,)

    videos = []
    with urllib.request.urlopen(videoFetchUrl) as url:
        data = json.loads(url.read().decode())
        for video in data['items']:
            video['snippet']['publishedAt'] = dateutil.parser.parse(video['snippet']['publishedAt'])
    return render(request, 'youtube/videos.html', {'videos': data['items']})


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
        youtube = googleapiclient.discovery.build(
            API_SERVICE_NAME, API_VERSION, credentials=credentials)

        channels = youtube.channels().list(mine=True, part='snippet').execute()
        myChannelId = channels["items"][0]["id"]
        sc['myChannelId'] = myChannelId
    else:
        myChannelId = sc['myChannelId']

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
    myComments = sorted(myComments, key=lambda k: k['snippet']['publishedAt'], reverse=True)
    print(myComments[:3])
    return render(request, 'youtube/comments.html', {'comments': myComments})

def get_video_comments(request, video_id):
    youtube = googleapiclient.discovery.build(API_SERVICE_NAME, API_VERSION, developerKey = DEVELOPER_KEY)
    comments = get_comments_from_video(youtube, video_id)
    return render(request, 'youtube/comments.html', {'comments': comments, 'video_id': video_id})

def get_comments_from_video(youtube, video_id):
    comments = []
    vid_stats = youtube.videos().list(part="statistics", id=video_id).execute()
    comment_count = vid_stats.get("items")[0].get("statistics").get("commentCount")
    if (comment_count and int(comment_count)>0):
        video_response = youtube.commentThreads().list(part="snippet", videoId=video_id, textFormat="plainText").execute()
        # Get the first set of comments
        for item in video_response['items']:
            # Extracting comments
            comment = item['snippet']['topLevelComment']
            comment['snippet']['publishedAt'] = dateutil.parser.parse(comment['snippet']['publishedAt'])
            if (item['snippet']['totalReplyCount'] > 0):
                replies = get_replies(youtube, item['id'])
                comment['replies'] = replies
            comments.append(comment)

        # Keep getting comments from the following pages
        while ("nextPageToken" in video_response):
            video_response = youtube.commentThreads().list(part="snippet", videoId=video_id, pageToken=video_response["nextPageToken"], textFormat="plainText").execute()
            for item in video_response['items']:
                # Extracting comments    
                comment = item['snippet']['topLevelComment']
                comment['snippet']['publishedAt'] = dateutil.parser.parse(comment['snippet']['publishedAt'])
                if (item['snippet']['totalReplyCount'] > 0):
                    replies = get_replies(youtube, item['id'])
                    comment['replies'] = replies
                comments.append(comment)
    return comments


def get_replies(youtube, parent_id):
    results = youtube.comments().list(part="snippet", parentId=parent_id, textFormat="plainText").execute()
    replies = []
    for item in results['items']:
        reply = item['snippet']
        reply['publishedAt'] = dateutil.parser.parse(item['snippet']['publishedAt'])
        replies.append(reply)
    return replies

def credentials_to_dict(credentials):
  return {'token': credentials.token,
          'refresh_token': credentials.refresh_token,
          'token_uri': credentials.token_uri,
          'client_id': credentials.client_id,
          'client_secret': credentials.client_secret,
          'scopes': credentials.scopes}


def index_comments(comments):
    print(comments)

if __name__ == '__main__':
    # When running locally, disable OAuthlib's HTTPs verification.
    # ACTION ITEM for developers:
    #     When running in production *do not* leave this option enabled.
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
