# -*- coding: utf-8 -*-`
"""api.py - Create and configure the Game API exposing the resources.
This can also contain game logic. For more complex games it would be wise to
move game logic to another file. Ideally the API will be simple, concerned
primarily with communication to/from the API's users."""


import logging
import endpoints
import xml.etree.ElementTree as ET
from boggle import word_points
from protorpc import remote, messages
from google.appengine.api import memcache
from google.appengine.api import taskqueue
from google.appengine.api import urlfetch
from google.appengine.ext import ndb
from models import User, Game
from models import StringMessage, NewGameForm, GameForm, MakeMoveForm,\
    UserGameForms, EndGameForm
from utils import get_by_urlsafe

#  ## --- Resource Container Configuration --- ###  #
NEW_GAME_REQUEST = endpoints.ResourceContainer(NewGameForm)
GET_GAME_REQUEST = endpoints.ResourceContainer(
    urlsafe_game_key=messages.StringField(1),)
USER_GAMES_REQUEST = endpoints.ResourceContainer(
    urlsafe_user_key=messages.StringField(1),)
MAKE_MOVE_REQUEST = endpoints.ResourceContainer(
    MakeMoveForm,
    urlsafe_game_key=messages.StringField(1),)
USER_REQUEST = endpoints.ResourceContainer(
                    user_name=messages.StringField(1),
                    email=messages.StringField(2),)
CANCEL_GAME_REQUEST = endpoints.ResourceContainer(
                            user_name=messages.StringField(1),
                            urlsafe_game_key=messages.StringField(2),)


MEMCACHE_MOVES_REMAINING = 'MOVES_REMAINING'


#  ## --- Endpoints  --- ##  #
@endpoints.api(name='boggle', version='v1')
class BoggleApi(remote.Service):
    """Game API"""
    @endpoints.method(request_message=USER_REQUEST,
                      response_message=StringMessage,
                      path='user',
                      name='create_user',
                      http_method='POST')
    def create_user(self, request):
        """Create a User. Requires a unique username"""
        if User.query(User.name == request.user_name).get():
            raise endpoints.ConflictException(
                    'A User with that name already exists!')
        user = User(name=request.user_name, email=request.email)
        user.put()
        return StringMessage(message='User {} created!'.format(
                request.user_name))

    @endpoints.method(request_message=NEW_GAME_REQUEST,
                      response_message=GameForm,
                      path='game',
                      name='new_game',
                      http_method='POST')
    def new_game(self, request):
        """Creates new game"""
        user1_name = request.user1_name
        user1 = User.query(User.name == request.user1_name).get()
        if not user1:
            raise endpoints.NotFoundException(
                    'A User named %s does not exist!' % user1_name)
        user2_name = request.user2_name
        user2 = User.query(User.name == request.user2_name).get()
        if not user2:
            raise endpoints.NotFoundException(
                    'A User named %s does not exist!' % user2_name)
        try:
            game = Game.new_game(user1.key, user2.key, request.turns)
            # print user1.key, user2.key
            user1.games.append(game.key)
            user2.games.append(game.key)
        except:
            raise endpoints.BadRequestException('Bad request')
        else:
            user1.put()
            user2.put()
        # Use a task queue to update the average turns remaining.
        # This operation is not needed to complete the creation of a new game
        # so it is performed out of sequence.
        # taskqueue.add(url='/tasks/cache_average_turns')

        return game.to_form('Good luck playing biggle!')

    @endpoints.method(request_message=GET_GAME_REQUEST,
                      response_message=GameForm,
                      path='game/{urlsafe_game_key}',
                      name='get_game',
                      http_method='GET')
    def get_game(self, request):
        """Return the current game state."""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if game is not None:
            return game.to_form('Time to make a move!')
        else:
            raise endpoints.NotFoundException('Game not found!')

    @endpoints.method(request_message=MAKE_MOVE_REQUEST,
                      response_message=GameForm,
                      path='game/{urlsafe_game_key}',
                      name='make_move',
                      http_method='PUT')
    def make_move(self, request):
        """Makes a move. Returns a game state with message"""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if game.game_over:
            return game.to_form('Game already over!')
        user_name = request.user_name        
        user = User.query(User.name == request.user_name).get()
        if user is None:
            return game.to_form('Player not found.')
        if user.key not in [game.user1, game.user2]:
            return game.to_form('You\'re not playing in this game')

        # Make sure it is this user's turn
        whose_turn = game.user2
        if game.user1_is_next:
            whose_turn = game.user1
        if user.key != whose_turn:
            return game.to_form('It\'s not your turn')
        # All these checks have passed, so the turn can proceed, and the game 
        # will be updated:
        game.user1_is_next = not game.user1_is_next
        game.turns_remaining -= 1
        msg = ""
        # make the submitted word all caps for checking.
        guess = request.guess.upper()
        # Check that the word is in the dictionary:
        dictionary_url = "http://www.dictionaryapi.com"\
                         "/api/v1/references/collegiate/xml/{word}?key={key}"
        dict_lookup = urlfetch.Fetch(
            dictionary_url.format(word=guess,
                                  key='a910e27f-cb8e-4d10-9a2d-b8bf3530c02d')
        )
        # The Merriam-Webster API returns an XML string. If the word is found
        # the XML will contain an <entry> tag.
        # This makes us of the ElementTree XML API module
        # https://docs.python.org/2.7/library/xml.etree.elementtree.html
        parsed_xml = ET.fromstring(dict_lookup.content)
        entry = parsed_xml.find('entry')
        if entry is None:
            msg += 'Sorry! "{}" is not in the english dictionary'.format(guess)
        # Check that this word hasn't already been found
        elif guess in game.words_found:
            msg +='Sorry! "{}" that word has already been found'.format(guess)
        # Check that the word can be found on the board
        elif not game.check_word(guess):
            msg += 'Sorry! The word "{}" is not in the board.'.format(guess)
        else:
            # The word passes all our checks
            # calculate and add points to the users's total for this game
            points = word_points(guess)
            game.words_found.append(guess)
            if user.key == game.user1:
                game.user1_points += points
            else:
                game.user2_points += points
            msg += 'Correct! {} points for the word "{}"'.format(points, guess)
        game.put()
        if game.turns_remaining < 1:
            game.turns_remaining = 0
            w, l = game.end_game(False)
            msg += "{} wins!".format(w.get().name)
            return game.to_form(msg + ' Game over!')
        else:
            return game.to_form(msg)

    @endpoints.method(response_message=StringMessage,
                      path='games/average_turns',
                      name='get_average_turns_remaining',
                      http_method='GET')
    def get_average_turns(self, request):
        """Get the cached average moves remaining"""
        return StringMessage(
            message=memcache.get(MEMCACHE_MOVES_REMAINING) or '')

    @endpoints.method(request_message=CANCEL_GAME_REQUEST,
                      response_message=GameForm,
                      path='games/{urlsafe_game_key}/cancel',
                      name='cancel_game',
                      http_method='PUT')
    def cancel_game(self, request):
        """Allow a user to forfeit by cancelling a game"""        
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if game.game_over:
            return game.to_form('Game already over!')
        user = User.query(User.name == request.user_name).get()
        if game.key not in user.games:
            return game.to_form('Only the participants can cancel a game')
        # make the other user the winner
        w, l = game.end_game(cancelled_by=user.key)
        winner = w.get()
        loser = l.get()
        return game.to_form("{} cancelled the game. {} wins!"
                            .format(loser.name, winner.name))

    @endpoints.method(request_message=USER_GAMES_REQUEST,
                      response_message=UserGameForms,
                      path='user/{urlsafe_user_key}',
                      name='get_user_games',
                      http_method='GET')
    def get_user_games(self, request):
        """Return the a list of game states for a user ."""
        user = get_by_urlsafe(request.urlsafe_user_key, User)
        if user is not None:
            games_list = []
            for index, key in enumerate(user.games):
                # game_key = ndb.Key(urlsafe=key)
                # games_list.append(game_key.get())
                try:
                    game_key = ndb.Key(urlsafe=key)    
                except TypeError as e:
                    print "Type error on index {}: {} ".format(index, e)
                else:
                    games_list.append(game_key.get())
            return UserGameForms(
                user=user.to_form(),
                games=[game.to_form('{name} is a player in this game'.
                                    format(name=user.name)) for game in games_list
                       ])
        else:
            raise endpoints.NotFoundException('User not found!')

    @staticmethod
    def _cache_average_turns():
        """Populates memcache with the average moves remaining of Games"""
        games = Game.query(Game.game_over == False).fetch()
        if games:
            count = len(games)
            total_turns_remaining = sum([game.turns_remaining
                                        for game in games])
            average = float(total_turns_remaining)/count
            memcache.set(MEMCACHE_MOVES_REMAINING,
                         'The average moves remaining is {:.2f}'.format(average))


api = endpoints.api_server([BoggleApi])
