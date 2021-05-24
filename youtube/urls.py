from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from .views import HomePageView
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('test', views.test_api_request, name='test'),
    path('authorize', views.authorize, name='authorize'),
    path('oauth2callback', views.oauth2callback, name='oauth2callback'),
    path('revoke', views.revoke, name='revoke'),
    path('clear', views.clear_credentials, name='clear'),
    path('get_comments', views.get_comments, name='get_comments'),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

