from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from .views import HomePageView
from . import views
from . import views_api

app_name = 'youtube'
urlpatterns = [
  path('', views.create_word_filter, name='home'),

  path('test', views.test_api_request, name='test'),
  path('authorize', views.authorize, name='authorize'),
  path('oauth2callback', views.oauth2callback, name='oauth2callback'),
  path('revoke', views.revoke, name='revoke'),
  path('clear', views.clear_credentials, name='clear'),
  path('get_comments', views.get_comments, name='get_comments'),
  path('get_videos', views.get_videos, name='get_videos'),
  path('get_video_comments/<str:video_id>', views.get_video_comments, name='get_video_comments'),
  path('backend', views.index, name='backend'),
  path('get_rule_collection_templates', views.get_rule_collection_templates, name='get_rule_collection_templates'),
  path('get_matching_comments/<str:phrase>', views.get_matching_comments, name='get_matching_comments'),

  path('api', views_api.api, name='api'),
  path('api/authenticate', views_api.getUserInfo),
  path('api/loadFilters', views_api.loadFilters),
  path('api/loadFilter', views_api.loadFilter),
  path('api/createFilter', views_api.createFilter),
  path('api/updateFilter', views_api.updateFilter),
  path('api/deleteFilter', views_api.deleteFilter),

  path('api/previewRule/<int:rule_id>', views_api.previewRule),
  path('api/getComment/<int:comment_id>', views_api.getComment),
  path('api/previewFilter/<int:filter_id>', views_api.previewFilter),
]

if settings.DEBUG:
  urlpatterns += static(
    settings.STATIC_URL, document_root=settings.STATIC_ROOT)
  urlpatterns += static(
    settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
