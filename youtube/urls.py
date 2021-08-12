from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from django.conf.urls import url, include
from rest_framework import routers

from .views import HomePageView
from . import views
from . import views_api

router = routers.DefaultRouter()
router.register(r'collections', views_api.RuleCollectionViewSet)
router.register(r'commentTables/(?P<username>\d+)', views_api.CommentViewSet)
router.register(r'allCommentTables', views_api.AllCommentsViewSet)

app_name = 'youtube'
urlpatterns = [
  path('', views.home, name='home'),
  path('about_us', views.about_us, name='about_us'),  

  path('overview', views.overview),
  path('collection/new', views.create_word_filter),
  path('collection/<int:filter_id>/overview', views.overview_word_filter),
  path('collection/<int:filter_id>/edit', views.edit_word_filter),

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
  path('api/sync', views.sync),

  path('api', views_api.api, name='api'),
  path('api/debug', views_api.debug),
  path('api/authenticate', views_api.getUserInfo),


  # Filter related modifiers
  path('api/loadFilters', views_api.loadFilters),
  path('api/loadFilter', views_api.loadFilter),
  path('api/createFilter', views_api.createFilter),
  path('api/updateFilter', views_api.updateFilter),
  path('api/deleteFilter', views_api.deleteFilter),

  # Chart related stuff
  path('api/charts/overview', views_api.overviewChart),
  path('api/charts/filter/<int:filter_id>/overview', views_api.filterChart),
  path('api/charts/filter/<int:filter_id>/rule/<int:rule_id>', views_api.ruleChart),

  # Rule related modifiers
  path('api/previewRule', views_api.previewRule), # Preview rule is used to preview BEFORE a rule ID has been assigned
  path('api/previewFilter/<int:filter_id>', views_api.previewFilter),
  path('api/getComment/<int:comment_id>', views_api.getComment),
  path('api/updateRule', views_api.updateRule), # Preview rule is used to preview BEFORE a rule ID has been assigned

  # Django rest frameworks datatables
  path('capi/', include(router.urls)),
  path('capi/collection', views_api.indexRuleCollection, name='collections'),
  path('capi/commentTable/<int:filter_id>', views_api.indexCommentCollection, name='commentTables'),

  # Test
  path('mytest', views.mytest, name='mytest'),

]

if settings.DEBUG:
  urlpatterns += static(
    settings.STATIC_URL, document_root=settings.STATIC_ROOT)
  urlpatterns += static(
    settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
