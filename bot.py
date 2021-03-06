
import os
import message

import spotipy
import spotipy.util as util

from slackclient import SlackClient

# To remember which teams have authorized your app and what tokens are
# associated with each team, we can store this information in memory on
# as a global object. When your bot is out of development, it's best to
# save this in a more persistant memory store.
authed_teams = {}

USERNAME = 'firrstep'
SLACK_PLAYLIST_ID = '1oTqOl5VXjwVePqjKY5Otf'
ID_KEY_TERMS = "spotify"

class Bot(object):
    """ Instanciates a Bot object to handle Slack onboarding interactions."""
    def __init__(self):
        super(Bot, self).__init__()
        self.name = "pythonboardingbot"
        self.emoji = ":robot_face:"
        # When we instantiate a new bot object, we can access the app
        # credentials we set earlier in our local development environment.
        self.oauth = {"client_id": os.environ.get("CLIENT_ID"),
                      "client_secret": os.environ.get("CLIENT_SECRET"),
                      # Scopes provide and limit permissions to what our app
                      # can access. It's important to use the most restricted
                      # scope that your app will need.
                      "scope": "bot"}
        self.verification = os.environ.get("VERIFICATION_TOKEN")

        # NOTE: Python-slack requires a client connection to generate
        # an oauth token. We can connect to the client without authenticating
        # by passing an empty string as a token and then reinstantiating the
        # client with a valid OAuth token once we have one.
        self.client = SlackClient("")
        # We'll use this dictionary to store the state of each message object.
        # In a production envrionment you'll likely want to store this more
        # persistantly in  a database.
        self.messages = {}

    def auth(self, code):
        """
        Authenticate with OAuth and assign correct scopes.
        Save a dictionary of authed team information in memory on the bot
        object.

        Parameters
        ----------
        code : str
            temporary authorization code sent by Slack to be exchanged for an
            OAuth token

        """
        # After the user has authorized this app for use in their Slack team,
        # Slack returns a temporary authorization code that we'll exchange for
        # an OAuth token using the oauth.access endpoint
        auth_response = self.client.api_call(
            "oauth.access",
            client_id=self.oauth["client_id"],
            client_secret=self.oauth["client_secret"],
            code=code
        )
        # To keep track of authorized teams and their associated OAuth tokens,
        # we will save the team ID and bot tokens to the global
        # authed_teams object
        team_id = auth_response["team_id"]
        authed_teams[team_id] = {"bot_token":
                                 auth_response["bot"]["bot_access_token"]}
        # Then we'll reconnect to the Slack Client with the correct team's
        # bot token
        self.client = SlackClient(authed_teams[team_id]["bot_token"])


    def get_track_id(self, slack_event):
        try:
            import pdb
            pdb.set_trace()
            track_url = slack_event['event']['text']
            if ID_KEY_TERMS in track_url:
                if "track/" in track_url:
                    track = track_url.split("track/")
                else:
                    track = track_url.split("track:")
                clean_track = track[1].split(">")
                clean_track = clean_track[0]

                print "Found Track %s " % clean_track
                return clean_track

        except KeyError:
            print "no spotify link found, listening "
            return ''

    def add_track(self, slack_event):
        """
        Takes a slack event and adds the posted song to the playlist
        """
        track_id = self.get_track_id(slack_event)
        scope = 'playlist-modify-public'
        token = util.prompt_for_user_token(USERNAME, scope)

        if token:
            sp = spotipy.Spotify(auth=token)
            sp.trace = False
            results = sp.user_playlist_add_tracks(USERNAME, SLACK_PLAYLIST_ID, [track_id])
            print(results)
        else:
            print('Cannot get token for ' + USERNAME)
