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
#    return HttpResponse(print_index_table())
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

    channel = youtube.channels().list(mine=True, part='snippet').execute()

    # Save credentials back to session in case access token was refreshed.
    # ACTION ITEM: In a production app, you likely want to save these
    #              credentials in a persistent database instead.
    request.session['credentials'] = credentials_to_dict(credentials)
    return render(request, 'youtube/profile.html', channel)
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
        return HttpResponse('Credentials successfully revoked.' + print_index_table())
    else:
        return HttpResponse('An error occurred.' + print_index_table())

def clear_credentials(request):
    if 'credentials' in request.session:
        del request.session['credentials']
    return HttpResponse('Credentials have been cleared.<br><br>' +
          print_index_table())

def get_comments(request):

    comments = []
    video_id = "uMWOVLFn218"

    youtube = googleapiclient.discovery.build(API_SERVICE_NAME, API_VERSION, developerKey = DEVELOPER_KEY)
    video_response = youtube.commentThreads().list(part="snippet", videoId=video_id, textFormat="plainText").execute()

    # iterate video response
    for item in video_response['items']:
        # Extracting comments
        comment = item['snippet']['topLevelComment']['snippet']['textDisplay']
        comments.append(comment)

    return render(request, 'youtube/comments.html', {'comments': comments})
    

def credentials_to_dict(credentials):
  return {'token': credentials.token,
          'refresh_token': credentials.refresh_token,
          'token_uri': credentials.token_uri,
          'client_id': credentials.client_id,
          'client_secret': credentials.client_secret,
          'scopes': credentials.scopes}

def print_index_table():
    return ('<table>' +
            '<tr><td><a href="/test">Test an API request</a></td>' +
            '<td>Submit an API request and see a formatted JSON response. ' +
            '    Go through the authorization flow if there are no stored ' +
            '    credentials for the user.</td></tr>' +
            '<tr><td><a href="/authorize">Test the auth flow directly</a></td>' +
            '<td>Go directly to the authorization flow. If there are stored ' +
            '    credentials, you still might not be prompted to reauthorize ' +
            '    the application.</td></tr>' +
            '<tr><td><a href="/revoke">Revoke current credentials</a></td>' +
            '<td>Revoke the access token associated with the current user ' +
            '    session. After revoking credentials, if you go to the test ' +
            '    page, you should see an <code>invalid_grant</code> error.' +
            '</td></tr>' +
            '<tr><td><a href="/clear">Clear Flask session credentials</a></td>' +
            '<td>Clear the access token currently stored in the user session. ' +
            '    After clearing the token, if you <a href="/test">test the ' +
            '    API request</a> again, you should go back to the auth flow.' +
            '</td></tr></table>')


if __name__ == '__main__':
    # When running locally, disable OAuthlib's HTTPs verification.
    # ACTION ITEM for developers:
    #     When running in production *do not* leave this option enabled.
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
