from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from .views import HomePageView
from . import views
from . import views_filters
from . import views_rules

app_name = 'youtube'
urlpatterns = [
    path('', views.create_word_filter, name='home'),
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
    path('get_rule_collection_templates', views.get_rule_collection_templates, name='get_rule_collection_templates'),
    path('get_matching_comments/<str:phrase>', views.get_matching_comments, name='get_matching_comments'),    

    path('loadFilters', views_filters.loadFilters),
    path('loadFilter/<int:filter_id>', views_filters.loadFilter),
    path('createFilter', views_filters.createFilter),
    path('updateFilter', views_filters.updateFilter),
    path('deleteFilter/<int:filter_id>', views_filters.deleteFilter),

    path('previewRule/<int:rule_id>', views_rules.previewRule),    
    path('getComment/<int:comment_id>', views_rules.getComment),   
    path('previewFilter/<int:filter_id>', views_rules.previewFilter),     


]

if settings.DEBUG:
    urlpatterns += static(
        settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

