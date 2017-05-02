from dotenv import Dotenv

import json

import requests

class CacheToken:
    def __init__(self):
        self.yelp_id, self.yelp_secret = Dotenv.dotenv()
        self.api_url = 'https://api.yelp.com/oauth2/token'

    def get_token(self):
        res = requests.post(self.api_url, data={'client_id': self.yelp_id,
            'client_secret': self.yelp_secret})
        token = json.loads(res.text)
        return token['access_token'], token['expires_in'], token['token_type']

#def check_token(token=None):
#    if token == 0:
#        token, expires_in, token_type = get_token()
#        start_time = int(time.time())
#    else:
#        if start_time + valid_for < int(time.time()):
#            token, expires_in, token_type = get_token()
#            start_time = int(time.time())
#
