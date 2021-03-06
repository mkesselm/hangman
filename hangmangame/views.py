from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views import generic
from django.views.generic import View, FormView
from django.contrib.messages.views import SuccessMessageMixin
from .models import Gamestate, Player
from .forms import LogInForm, GuessForm
from .images import hangman_images_list


def parse_player_name(path):
    # find the player_name by parsing the tail of the request's url; either this
    # or overloading the SuccessMessageMixin--which I don't have a good grasp of
    # yet--are necessary to pass information between view classes
    i = -2
    c = ''
    while c != '/':
        c = path[i]
        i -= 1
    i += 2
    return path[len(path)+i:len(path)-1]


def get_current_gamestate(player_name):
    return Player.objects.get(pk=player_name).gamestate_set.last()


def login(request, form):
    player_name = form.cleaned_data.get('player_name')
    # success_message = "%(player_name)s"
    if(Player.objects.filter(pk=player_name)):
        # player_name exists
        # retrieve the current game's bad guess count and redirect
        return HttpResponseRedirect(reverse('hangmangame:match',
        args=(player_name,)))
    else:
        # player_name does not exist
        # create a new player_name, a new gamestate, save them to the db, and
        # redirect
        p = Player(player_name)
        p.save()
        g = Gamestate()
        g.reset()
        g.owner_id = p.pk
        g.save()
        return HttpResponseRedirect(reverse('hangmangame:match',
        args=(player_name,)))


class IndexView(FormView):
    template_name = 'hangmangame/index.html'
    form_class = LogInForm
    model = Player

    def get_queryset(self):
        return Player.objects.all()
    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            return login(request, form)


class MatchView(FormView):
    model = Player
    template_name = 'hangmangame/match.html'
    form_class = GuessForm
    gamestate = Gamestate

    def get(self, request, *args, **kwargs):
        player_name = parse_player_name(request.path)
        current_gamestate = get_current_gamestate(player_name)
        form = self.form_class()
        return render(request, self.template_name, {'form': form,
        'model': Player.objects.get(pk=player_name),
        'gamestate': current_gamestate,
        'hangman_image': hangman_images_list[
        current_gamestate.bad_guess_counter],})

    def post(self, request, *args, **kwargs):
        player_name = parse_player_name(request.path)
        current_gamestate = get_current_gamestate(player_name)
        form = self.form_class(request.POST)
        if form.is_valid():
            letter = form.cleaned_data.get('guess')
            return current_gamestate.guess(request, letter)


class StatsView(generic.DetailView):
    model = Player
    template_name = 'hangmangame/stats.html'

    def get(self, request, *args, **kwargs):
        player_name = parse_player_name(request.path)
        get_object_or_404(Player, pk=player_name)
        return render(request, 'hangmangame/stats.html',
        {'player': Player.objects.get(pk=player_name),})
