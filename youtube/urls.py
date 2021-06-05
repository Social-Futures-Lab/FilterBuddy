from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from .views import HomePageView
from . import views

app_name = 'youtube'
urlpatterns = [
    path('', views.create_word_filter, name='create_word_filter'),
    path('api', views.api, name='api'),
    path('test', views.test_api_request, name='test'),
    path('authorize', views.authorize, name='authorize'),
    path('oauth2callback', views.oauth2callback, name='oauth2callback'),
    path('revoke', views.revoke, name='revoke'),
    path('clear', views.clear_credentials, name='clear'),
    path('get_comments', views.get_comments, name='get_comments'),
    path('get_videos', views.get_videos, name='get_videos'),
    path('get_video_comments/<str:video_id>', views.get_video_comments, name='get_video_comments'),
    path('backend', views.index, name='backend'),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

