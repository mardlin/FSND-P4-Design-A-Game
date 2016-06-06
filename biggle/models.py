"""models.py - This file contains the class definitions for the Datastore
entities used by the Game. Because these classes are also regular Python
classes they can include methods (such as 'to_form' and 'new_game')."""

import random
import json
import boggle
import generate_board
from decimal import Decimal
from datetime import date
from protorpc import messages
from google.appengine.ext import ndb


class User(ndb.Model):
    """User profile"""
    name = ndb.StringProperty(required=True)
    email = ndb.StringProperty()
    games = ndb.PickleProperty(required=True, default=[""])
    wins = ndb.IntegerProperty(required=True, default=0)
    losses = ndb.IntegerProperty(required=True, default=0)

    def to_form(self):
        """Returns a GameForm representation of the Game"""
        form = UserForm()
        form.urlsafe_key = self.key.urlsafe()
        form.name = self.name
        return form

    def win_percentage(self):
        if self.wins + self.losses < 1:
            return float(0)
        else:
            percentage = Decimal(self.wins)/Decimal((self.wins+self.losses))
            p = round(percentage, 3)
            return float(p)

    def to_performance_form(self):
        form = UserPerformanceForm()
        form.name = self.name
        form.win_percentage = self.win_percentage()
        form.wins = self.wins
        form.losses = self.losses
        form.urlsafe_key = self.key.urlsafe()
        return form


class Game(ndb.Model):
    """Game object"""
    user1 = ndb.KeyProperty(required=True, kind='User')
    user2 = ndb.KeyProperty(required=True, kind='User')
    board = ndb.PickleProperty(required=True)  # NxN list of letters
    user1_points = ndb.IntegerProperty(required=True, default=0)
    user2_points = ndb.IntegerProperty(required=True, default=0)
    words_found = ndb.PickleProperty(required=True, default=[])
    turns_allowed = ndb.IntegerProperty(required=True)
    turns_remaining = ndb.IntegerProperty(required=True)
    user1_is_next = ndb.BooleanProperty(required=True, default=True)
    game_over = ndb.BooleanProperty(required=True, default=False)
    game_cancelled = ndb.BooleanProperty(required=True, default=False)
    winner = ndb.KeyProperty(kind='User')
    history = ndb.PickleProperty(required=True, default=[])

    @classmethod
    def new_game(cls, user1, user2, turns):
        """Creates and returns a new game"""
        # generate a 4x4 board
        board = generate_board.board()

        game = Game(board=board,
                    user1=user1,
                    user2=user2,
                    words_found=[],
                    user1_is_next=True,
                    turns_allowed=turns,
                    turns_remaining=turns,
                    game_over=False)
        game.put()
        return game

    def check_word(self, word):
        """Returns a boolean value indicating whether the word
        can actually be constructed from the board.
        """
        # use the boggle.find_letters() method to get a list of the coords
        # of the words
        word_coords = boggle.find_letters(word, self.board)
        # check for a continuous path among thos coordinates
        return boggle.all_paths(word, word_coords)

    def to_form(self, message):
        """Returns a GameForm representation of the Game"""
        form = GameForm()
        form.urlsafe_key = self.key.urlsafe()
        form.user1_name = self.user1.get().name
        form.user2_name = self.user2.get().name
        form.user1_points = self.user1_points
        form.user2_points = self.user2_points
        form.user1_is_next = self.user1_is_next
        form.turns_remaining = self.turns_remaining
        form.board = json.dumps(self.board)
        form.words_found = json.dumps(self.words_found)
        form.game_over = self.game_over
        form.message = message
        if self.winner is not None:
            form.winner = self.winner.get().name
        return form

    def enter_history(self, user, message):
        self.history.append({
            'user': user.name,
            'message': message
            })
        self.put()

    def end_game(self, cancelled_by=None):
        """Ends the game - if won is True, the player won. - if won is False,
        the player lost."""
        if cancelled_by is not None:
            #  make the non-cancelling user the winner
            if (cancelled_by == self.user2):
                w, l = self.user1, self.user2
            else:
                w, l = self.user2, self.user1
        # else the game ended because turns_remaining<1
        elif self.user1_points > self.user2_points:
            w, l = self.user1, self.user2
        elif self.user2_points > self.user1_points:
            w, l = self.user1, self.user2
        else:
            # players are tied
            w, l = None, None
        # update user entities and the game entity accordingly
        winning_user = w.get()
        winning_user.wins += 1
        winning_user.put()
        losing_user = l.get()
        losing_user.losses += 1
        losing_user.put()
        self.winner = w
        self.game_over = True
        self.put()
        return w, l


class UserForm(messages.Message):
    urlsafe_key = messages.StringField(1, required=True)
    name = messages.StringField(2, required=True)


class UserPerformanceForm(messages.Message):
    name = messages.StringField(1, required=True)
    win_percentage = messages.FloatField(2, required=True)
    wins = messages.IntegerField(3, required=True)
    losses = messages.IntegerField(4, required=True)
    urlsafe_key = messages.StringField(5, required=True)


class UserPerformanceForms(messages.Message):
    users = messages.MessageField(UserPerformanceForm, 1, repeated=True)


class GameForm(messages.Message):
    """GameForm for outbound game state information"""
    urlsafe_key = messages.StringField(1, required=True)
    message = messages.StringField(2, required=True)
    turns_remaining = messages.IntegerField(3, required=True)
    user1_name = messages.StringField(4, required=True)
    user1_points = messages.IntegerField(5, required=True)
    user2_name = messages.StringField(6, required=True)
    user2_points = messages.IntegerField(7, required=True)
    user1_is_next = messages.BooleanField(8, required=True)
    game_over = messages.BooleanField(9, required=True)
    board = messages.StringField(10)
    words_found = messages.StringField(11)
    winner = messages.StringField(12)


class UserGameForms(messages.Message):
    """Return multiple GameForms for a User"""
    user = messages.MessageField(UserForm, 1)
    games = messages.MessageField(GameForm, 2, repeated=True)


class NewGameForm(messages.Message):
    """Used to create a new game"""
    user1_name = messages.StringField(1, required=True)
    user2_name = messages.StringField(2, required=True)
    turns = messages.IntegerField(3, default=20)


class MakeMoveForm(messages.Message):
    """Used to make a move in an existing game"""
    user_name = messages.StringField(1, required=True)
    guess = messages.StringField(2, required=True)


class GameHistoryForm(messages.Message):
    game = messages.MessageField(GameForm, 1, required=True)
    turns = messages.StringField(2, repeated=True)


class StringMessage(messages.Message):
    """StringMessage-- outbound (single) string message"""
    message = messages.StringField(1, required=True)
