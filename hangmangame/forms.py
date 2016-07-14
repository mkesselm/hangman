from django import forms
from .models import Player, Gamestate

class LogInForm(forms.Form):
    player_name = forms.CharField(label='Username', max_length=100)

class GuessForm(forms.Form):
    guess = forms.CharField(label='Letter', max_length=1)

    # class Meta:
    #     model = Gamestate
    #     fields = ('player_name', 'guess',)
