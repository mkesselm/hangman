from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views import generic
from django.views.generic import View, FormView
from django.contrib.messages.views import SuccessMessageMixin

from .models import Gamestate, Player
from .forms import LogInForm, GuessForm

# list of ascii images passed to client during gameplay
# N.B. template using entries from this list must use the <pre>...</pre> notation or this will show up as gibberish
hangman_images_list = [
    # 0
    '',
    # 1
    '_______________________________\n|                             |\n-------------------------------',
    # 2
    '               |||\n               |||\n               |||\n               |||\n               |||\n               |||\n               |||\n               |||\n               |||\n               |||\n               |||\n               |||\n               |||\n               |||\n               |||\n               |||\n_______________________________\n|                             |\n-------------------------------',
    # 3
    '               ============\n               |||\n               |||\n               |||\n               |||\n               |||\n               |||\n               |||\n               |||\n               |||\n               |||\n               |||\n               |||\n               |||\n               |||\n               |||\n               |||\n_______________________________\n|                             |\n-------------------------------',
    # 4
    '               ============\n               |||        |\n               |||        |\n               |||        |\n               |||        |\n               |||        |\n               |||        |\n               |||\n               |||\n               |||\n               |||\n               |||\n               |||\n               |||\n               |||\n               |||\n               |||\n_______________________________\n|                             |\n-------------------------------',
    # 5
    '               ============\n               |||        |\n               |||        |\n               |||        |\n               |||        |\n               |||        |\n               |||        |\n               |||        _\n               |||      /oo\\\n               |||      \\  /\n               |||        -\n               |||\n               |||\n               |||\n               |||\n               |||\n               |||\n_______________________________\n|                             |\n-------------------------------',
    # 6
    '               ============\n               |||        |\n               |||        |\n               |||        |\n               |||        |\n               |||        |\n               |||        |\n               |||        _\n               |||      /oo\\\n               |||      \\ ^/\n               |||       --\n               |||     | || |\n               |||     | || |\n               |||     0 || 0\n               |||\n               |||\n               |||\n               |||\n               |||\n               |||\n_______________________________\n|                             |\n-------------------------------',
    # 7
    '               ============\n               |||        |\n               |||        |\n               |||        |\n               |||        |\n               |||        |\n               |||        |\n               |||        _\n               |||      /oo\\\n               |||      \\ ^/\n               |||       --\n               |||     | || |\n               |||     | || |\n               |||     0 || 0\n               |||      |  |\n               |||      |  |\n               |||      b  b\n               |||\n               |||\n               |||\n_______________________________\n|                             |\n-------------------------------',
    # 8
    '               ============\n               |||        |\n               |||        |\n               |||        |\n               |||        |\n               |||        |\n               |||        |\n               |||        _\n               |||      /oo\\\n               |||      \\ ^/\n               |||       --\n               |||     | || |\n               |||     | || |\n               |||     0 || 0\n               |||      |  |\n               |||      |  |\n               |||      b  b\n               |||      ----\n               |||    | |___|\n               |||    |..|___|\n_______________________________\n|                             |\n-------------------------------',
    # 9
    '               ============\n               |||        |\n               |||        |\n               |||        |\n               |||        |\n               |||        |\n               |||        |\n               |||        _\n               |||      /oo\\\n               |||      \\ O/\n               |||       --\n               |||     | || |\n               |||     | || |\n               |||     0 || 0\n               |||      |  |\n               |||      |  |\n               |||      b  b\n               |||\n               |||\n               |||\n_______________________________\n|                             |\n-------------------------------',
    # 10
    '               ============\n               |||        |\n               |||        |\n               |||        |\n               |||        |\n               |||        |\n               |||        |\n               |||        _\n               |||      /xx\\\n               |||      \\ ,/\n               |||       --\n               |||      /||\\\n               |||     | || |\n               |||     0 || 0\n               |||      |  |\n               |||      |  |\n               |||      b  b\n               |||\n               |||\n               |||\n_______________________________\n|                             |\n-------------------------------',
]

def parse_player_name(path):
    # find the player_name by parsing the tail of the request's url; either this or overloading the SuccessMessageMixin--which I don't have a good grasp of yet--are necessary to pass information between view classes
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
    success_message = "%(player_name)s"
    print(player_name.upper()) #DEBUG
    if(Player.objects.filter(pk=player_name)):
        # player_name exists
        # retrieve the current game's bad guess count and redirect
        return HttpResponseRedirect(reverse('hangmangame:match', args=(player_name,)))
    else:
        # player_name does not exist
        # create a new player_name, a new gamestate, save them to the db, and redirect
        p = Player(player_name)
        p.save()
        g = Gamestate()
        g.reset()
        g.owner_id = p.pk
        g.save()
        return HttpResponseRedirect(reverse('hangmangame:match', args=(player_name,)))

def guess(request, gamestate, letter):
    # check letter against the passed gamestate and win/lose/loop accordingly
    gamestate.fill_in_guess(letter)
    gamestate.save()
    guess_count = gamestate.bad_guess_counter
    # Now run through win/loss/loop-logic and redirect accordingly
    if gamestate.game_won():
        player_entry = get_object_or_404(Player, pk=gamestate.owner)
        player_entry.played_games += 1
        player_entry.save()
        gamestate.reset()
        gamestate.save()
        return render(request, 'hangmangame/matchWon.html', {'gamestate': gamestate,})
    elif gamestate.bad_guess_counter >= 10:
        player_entry = get_object_or_404(Player, pk=gamestate.owner)
        player_entry.played_games += 1
        player_entry.save()
        old_gamestate = gamestate
        gamestate.reset()
        gamestate.save()
        return render(request, 'hangmangame/matchLoss.html', {'gamestate': old_gamestate, 'hanged_man': hangman_images_list[10],})
    else:
        print(gamestate.owner_id)
        return HttpResponseRedirect(reverse('hangmangame:match', args=(gamestate.owner,)))

class IndexView(FormView):
    template_name = 'hangmangame/index.html'
    form_class = LogInForm
    initial = {'key':'value'}
    model = Player

    def get_queryset(self):
        return Player.objects.all()
    def get(self, request, *args, **kwargs):
        form = self.form_class(initial=self.initial)
        return render(request, self.template_name, {'form': form})
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            return login(request, form)

class MatchView(FormView):
    model = Player
    template_name = 'hangmangame/match.html'
    form_class = GuessForm
    initial = {'key':'value', 'player_name': model,}
    gamestate = Gamestate

    def get(self, request, *args, **kwargs):
        player_name = parse_player_name(request.path)
        current_gamestate = get_current_gamestate(player_name)
        form = self.form_class(initial=self.initial)
        return render(request, self.template_name, {'form': form, 'model': Player.objects.get(pk=player_name), 'gamestate': current_gamestate, 'hangman_image': hangman_images_list[current_gamestate.bad_guess_counter],})

    def post(self, request, *args, **kwargs):
        player_name = parse_player_name(request.path)
        # print('MATCH RECEIVED POST' + player_name.upper())
        form = self.form_class(request.POST)
        if form.is_valid():
            letter = form.cleaned_data.get('guess')
            return guess(request, get_current_gamestate(player_name), letter)

class StatsView(generic.DetailView):
    model = Player
    template_name = 'hangmangame/stats.html'

    def get(self, request, *args, **kwargs):
        player_name = parse_player_name(request.path)
        get_object_or_404(Player, pk=player_name)
        return render(request, 'hangmangame/stats.html', {'player': Player.objects.get(pk=player_name),})
