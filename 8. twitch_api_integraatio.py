'''
@haeejuut
slink luokka kutsuja varten 
streamlink ja twitch api
'''
from streamlink import Streamlink, NoPluginError, PluginError
from twitchAPI.twitch import Twitch
from twitchAPI.oauth import UserAuthenticator
from twitchAPI.types import AuthScope
from twitchAPI.types import AuthType
from bs4 import BeautifulSoup
import sys
import json
import requests
import webbrowser


class StreamLinkSession():
    CLIENT_ID = ''
    CLIENT_SECRET = ''
    url = ''

    def __init__(self):
        # ladataan data
        self.load_data()
        # slink sessio olio
        self.session = Streamlink()
        self.session.set_loglevel("info")
        self.session.set_logoutput(sys.stdout)
        # twitch olio ja sen autentikointi
        self.twitch = Twitch(self.CLIENT_ID, self.CLIENT_SECRET)
        self.twitch.authenticate_app([])

    def load_data(self):
        '''
        Ladataan public.json ja private.json joista saadaan käyttäjän tiedot,
        sekä apin tarvitsemat avaimet.
        '''
        with open('public.json') as jfile:
            public_data = jfile.read()

        with open('private.json') as jfile:
            private_data = jfile.read()

        self.public_data = json.loads(public_data)
        self.private_data = json.loads(private_data)
        self.CLIENT_ID = self.public_data['CLIENT_ID']
        self.CLIENT_SECRET = self.private_data['CLIENT_SECRET']

    def authenticate(self):
        '''
        Autentikoi session
        '''
        target_scope = [AuthScope.BITS_READ, AuthScope.USER_READ_BROADCAST]
        auth = UserAuthenticator(self.twitch, target_scope, force_verify=False)
        # this will open your default browser and prompt you with auth
        token, refresh_token = auth.authenticate()
        # add User authentication
        self.twitch.set_user_authentication(token, target_scope)

# Käytettävät funktiot

    def fetch_stream(self, url):
        try:
            streams = self.session.streams(url)
            stream = streams['best']
            self.stream = stream
            self.url = stream.url
        except NoPluginError:
            print("Streamlink is unable to handle the URL '{0}'".format(url))
        except PluginError as err:
            print("Plugin error: {0}".format(err))

    def fetch_streams(self):        
        return self.twitch.get_streams(
            first=5
        )

    def get_username(self):
        pass

    def get_userID(self):
        user_info = self.twitch.get_users(logins=['my_username'])
        user_id = user_info['data'][0]['id']
        return user_id

    def tallenna(self, envtype, nimi):
        if envtype == '_nimi':
            self.public_data['NIMI'] = nimi
