"""utils.py - File for collecting general utility functions."""

import endpoints
from google.appengine.ext import ndb

from models import (
    User,
    Game
)


def games_and_users():
    """A helper function to identify unfinished games, and their users.
    Returns a 3-tuple of:
    0. the game,
    2. the user who has the next turn,
    3. the waiting user
    """
    open_games = Game.query(Game.game_over == False).fetch()
    games_list = []
    for game in open_games:
        if game.user1_is_next:
            # create a tuple for storing the next user and url safe game key
            games_list.append((game.key.urlsafe(),
                              game.user1.get(),
                              game.user2.get())
                              )
        else:
            games_list.append((game.key.urlsafe(),
                              game.user2.get(),
                              game.user1.get())
                              )
    return games_list


def get_by_urlsafe(urlsafe, model):
    """Returns an ndb.Model entity that the urlsafe key points to. Checks
        that the type of entity returned is of the correct kind. Raises an
        error if the key String is malformed or the entity is of the incorrect
        kind
    Args:
        urlsafe: A urlsafe key string
        model: The expected entity kind
    Returns:
        The entity that the urlsafe Key string points to or None if no entity
        exists.
    Raises:
        ValueError:"""
    try:
        key = ndb.Key(urlsafe=urlsafe)
    except TypeError:
        raise endpoints.BadRequestException('Invalid Key')
    except Exception, e:
        if e.__class__.__name__ == 'ProtocolBufferDecodeError':
            raise endpoints.BadRequestException('Invalid Key')
        else:
            raise

    entity = key.get()
    if not entity:
        return None
    if not isinstance(entity, model):
        raise ValueError('Incorrect Kind')
    return entity
