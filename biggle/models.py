"""models.py - This file contains the class definitions for the Datastore
entities used by the Game. Because these classes are also regular Python
classes they can include methods (such as 'to_form' and 'new_game')."""

import random
import json
import boggle
import generate_board
from datetime import date
from protorpc import messages
from google.appengine.ext import ndb


class User(ndb.Model):
    """User profile"""
    name = ndb.StringProperty(required=True)
    email = ndb.StringProperty()


class Game(ndb.Model):
    """Game object"""
    user1 = ndb.KeyProperty(required=True, kind='User')
    user2 = ndb.KeyProperty(required=True, kind='User')
    board = ndb.PickleProperty(required=True)  # NxN list of letters
    user1_points = ndb.IntegerProperty(required=True, default=0)
    user2_points = ndb.IntegerProperty(required=True, default=0)
    words_found = ndb.PickleProperty(required=True, default=["first"])
    turns_allowed = ndb.IntegerProperty(required=True)
    turns_remaining = ndb.IntegerProperty(required=True)
    user1_is_next = ndb.BooleanProperty(required=True, default=True)
    game_over = ndb.BooleanProperty(required=True, default=False)
    game_cancelled = ndb.BooleanProperty(required=True, default=False)

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
        return form

    def end_game(self, won=False):
        """Ends the game - if won is True, the player won. - if won is False,
        the player lost."""
        self.game_over = True
        self.put()
        # Add the game to the score 'board'
        score = Score(user=self.user, date=date.today(), won=won,
                      guesses=self.turns_allowed - self.turns_remaining)
        score.put()


class Score(ndb.Model):
    """Score object"""
    user = ndb.KeyProperty(required=True, kind='User')
    date = ndb.DateProperty(required=True)
    won = ndb.BooleanProperty(required=True)
    guesses = ndb.IntegerProperty(required=True)

    def to_form(self):
        return ScoreForm(user_name=self.user.get().name, won=self.won,
                         date=str(self.date), guesses=self.guesses)


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

    # scores



class NewGameForm(messages.Message):
    """Used to create a new game"""
    user1_name = messages.StringField(1, required=True)
    user2_name = messages.StringField(2, required=True)
    turns = messages.IntegerField(3, default=20)


class MakeMoveForm(messages.Message):
    """Used to make a move in an existing game"""
    user_name = messages.StringField(1, required=True)
    guess = messages.StringField(2, required=True)



class ScoreForm(messages.Message):
    """ScoreForm for outbound Score information"""
    user_name = messages.StringField(1, required=True)
    date = messages.StringField(2, required=True)
    won = messages.BooleanField(3, required=True)
    guesses = messages.IntegerField(4, required=True)


class ScoreForms(messages.Message):
    """Return multiple ScoreForms"""
    items = messages.MessageField(ScoreForm, 1, repeated=True)


class StringMessage(messages.Message):
    """StringMessage-- outbound (single) string message"""
    message = messages.StringField(1, required=True)
