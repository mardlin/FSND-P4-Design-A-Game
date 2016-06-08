#!/usr/bin/env python

"""main.py - This file contains handlers that are called by taskqueue and/or
cronjobs."""
import logging

import webapp2
from google.appengine.api import mail, app_identity
from api import BoggleApi

from models import User, Game


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


class SendWaitingUserReminderEmail(webapp2.RequestHandler):
    def get(self):
        """Send a reminder email to each User in an unfinished game.
        Called every 3 hours using a cron job"""
        app_id = app_identity.get_application_id()

        games_list = games_and_users()

        for game in games_list:
            urlsafe_game_key, next_user, waiting_user = game
            if waiting_user.email is None:
                pass
            else:
                subject = 'Your game isn\'t over yet!'
                body = '''Hello {a}, it\'s {b}\'s turn to find a word
                        in the game: {c}. Your turn will be next!'''.format(
                        a=waiting_user.name,
                        b=next_user.name,
                        c=urlsafe_game_key)
                # This will send test emails, the arguments to send_mail are:
                # from, to, subject, body
                mail.send_mail('noreply@{}.appspotmail.com'.format(app_id),
                               user.email,
                               subject,
                               body)
                print "email sent with subject: {}".format(subject)
                print "email sent with body: {}".format(body)


class SendNextUserReminderEmail(webapp2.RequestHandler):
    def get(self):
        """Send a reminder email to each User who has the next turn in a game.
        Called every hour using a cron job"""
        app_id = app_identity.get_application_id()

        # First find create a list of games that are not game over,
        # and the player whose turn it is in each of those games
        games_list = games_and_users()

        for game in games_list:
            urlsafe_game_key, next_user, waiting_user = game
            if next_user.email is None:
                pass
            else:
                subject = 'It\'s your turn!'
                body = '''Hello {a}, it\'s your turn to find a word
                        in the game: {b}! {c} is waiting for you!'''.format(
                        a=next_user.name,
                        b=urlsafe_game_key,
                        c=waiting_user.name)
                # This will send test emails, the arguments to send_mail are:
                # from, to, subject, body
                mail.send_mail('noreply@{}.appspotmail.com'.format(app_id),
                               next_user.email,
                               subject,
                               body)
                print "email sent with subject: {}".format(subject)
                print "email sent with body: {}".format(body)


class UpdateAverageMovesRemaining(webapp2.RequestHandler):
    def post(self):
        """Update game listing announcement in memcache."""
        BoggleApi._cache_average_turns()
        self.response.set_status(204)


app = webapp2.WSGIApplication([
    ('/crons/send_waiting_reminder', SendWaitingUserReminderEmail),
    ('/crons/send_next_reminder', SendNextUserReminderEmail),
    ('/tasks/cache_average_turns', UpdateAverageMovesRemaining),
], debug=True)
