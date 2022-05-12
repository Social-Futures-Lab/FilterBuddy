from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from django.conf.urls import url, include
from rest_framework import routers

# from .views import HomePageView
from . import views
from . import views_api

router = routers.DefaultRouter()
router.register(r'collections', views_api.RuleCollectionViewSet)
router.register(r'commentTables/(?P<username>\d+)', views_api.CommentViewSet)
router.register(r'allCommentTables', views_api.AllCommentsViewSet)

app_name = 'youtube'
urlpatterns = [
  path('', views.about_us, name='home'),
  path('log_in', views.home, name="login_user"),
  path('splash_page', views.about_us, name='splash_page'),

  path('overview', views.overview),
  path('collection/new', views.create_word_filter),
  path('collection/<int:filter_id>/overview', views.overview_word_filter),
  path('collection/<int:filter_id>/edit', views.edit_word_filter),

  path('authorize', views.authorize, name='authorize'),
  path('oauth2callback', views.oauth2callback, name='oauth2callback'),
  path('revoke', views.revoke, name='revoke'),
  path('clear', views.clear_credentials, name='clear'),
  path('sync', views.sync),

  path('api', views_api.api, name='api'),
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
  path('create_test_entries', views_api.createTestEntries, name='createTestEntries'),

]

if settings.LOCAL_DEBUG:
  urlpatterns += [
    path('fakelogin', views.fakelogin, name='fakelogin')
  ]

if settings.DEBUG:
  urlpatterns += static(
    settings.STATIC_URL, document_root=settings.STATIC_ROOT)
  urlpatterns += static(
    settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
