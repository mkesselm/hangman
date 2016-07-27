from django import forms
from .models import Player, Gamestate


class LogInForm(forms.Form):
    player_name = forms.CharField(
        label='Username', max_length=100, widget=forms.TextInput(attrs={
            'required': 'required',
            'autofocus': 'autofocus',
            }))


class GuessForm(forms.Form):
    guess = forms.CharField(label='Letter', max_length=1,
        widget=forms.TextInput(attrs={
            'required': 'required',
            'autofocus': 'autofocus',
            }))
