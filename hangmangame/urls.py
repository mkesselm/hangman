from django.conf.urls import url

from . import views
from .models import Player, Gamestate

app_name = 'hangmangame'
urlpatterns = [
    url(r'^$', views.IndexView.as_view(model = Player), name='index'),
    url(r'^match/(?P<pk>[\w\-]+)/$', views.MatchView.as_view(model = Player), name='match'),
    url(r'^stats/(?P<pk>[\w\-]+)/$', views.StatsView.as_view(model = Player), name='stats'),
    # url(r'^(?P<pk>[\w\-]+)/match/guess$', views.guess, name='guess'),
]
