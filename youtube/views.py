# -*- coding: utf-8 -*-

import os
import flask
import requests

import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery

from django.shortcuts import render
from django.views.generic import TemplateView

from django import forms
from django.views.generic.edit import FormView


class YouTubeForm(forms.Form):
    pass

class HomePageView(FormView):
    template_name = 'youtube/home.html'
    form_class = YouTubeForm

# Create your views here.

# This variable specifies the name of a file that contains the OAuth 2.0
# information for this application, including its client_id and client_secret.
CLIENT_SECRETS_FILE = "../../client_secret_youtube.json"

# This OAuth 2.0 access scope allows for full read/write access to the
# authenticated user's account and requires requests to use an SSL connection.
SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'


