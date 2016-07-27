import random
from django.core.urlresolvers import reverse
from django.db import models


# Player
#   contains
#       player_name: player's name
#       played_games: number of games completed
#
# each Player is associated with a single Gamestate
# max_length choice is relatively arbitrary
# TODO:
#   Some sort of authentication component
class Player(models.Model):
    player_name = models.CharField(max_length=100, primary_key=True,
                                   unique=True)

    played_games = models.IntegerField(default=0)

    games_lost = models.IntegerField(default=0)

    def __str__(self):
        return self.player_name

    def games_won(self):
        return self.played_games - self.games_lost


# Gamestate
#   contains
#       word_in_play: the word, as guessed so far, by the player
#       word_to_guess: the word the player is trying to guess
#       bad_guess_counter: the number of incorrect guess for this game so far
#       player: Player this Gamestate is associated with
#
# each Gamestate is associated with a single Player
# max_length is set to 45, as that is the longest word in the English language
# (see https://en.wikipedia.org/wiki/Longest_word_in_English)
class Gamestate(models.Model):
    word_in_play = models.CharField(max_length=45)

    word_to_guess = models.CharField(
        max_length=45, default=random.choice(
            open("words").read().splitlines()).lower())

    bad_guess_counter = models.IntegerField(default=0)

    owner = models.ForeignKey(Player, on_delete=models.CASCADE)

    guessed_letters = models.CharField(max_length=100, default='')

    def __str__(self):
        return self.word_to_guess

    def game_lost(self):
        return self.bad_guess_counter < 10

    def game_won(self):
        return self.word_to_guess == self.word_in_play

    def check_guess(self, guess):
        return guess in self.word_to_guess

    def fill_in_guess(self, guess):
        if guess not in self.guessed_letters:
            self.guessed_letters += guess
            if self.check_guess(guess):
                # create a list of indices of word_in_play to fill in by
                # matching the guess against word_to_guess
                entries = [
                    i for i,
                    entry in enumerate(self.word_to_guess) if entry == guess
                    ]
                # for each index generated in the list, fill in its location in
                # word_in_play as 'guess'
                for i in entries:
                    swap_list = list(self.word_in_play)
                    swap_list[i] = guess
                    self.word_in_play = ''.join(swap_list)
            else:
                self.bad_guess_counter += 1
            self.save()

    def reset(self):
        self.game_lost = False
        self.game_won = False
        self.bad_guess_counter = 0
        self.word_to_guess = random.choice(
        open("words").read().splitlines()).lower()
        self.word_in_play = ''.join([
            '#' for i in self.word_to_guess])
        self.guessed_letters = ''
