from flask import Flask, request, Response
from cache_token import CacheToken

import logging
from logging.handlers import RotatingFileHandler

import random
import re
import json
import time
from collections import namedtuple

import requests

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])

def alfred():
    #app.logger.warning('A warning occurred (%d apples)', 42)

    #check_token(0)

    #r = random.choice(['뭐 미친놈아', '어쩌라고'])
    if request.form['user_id'] != 'USLACKBOT':
        #text = '{{"text":"{} {}"}}'.format(request.form['text'], request.form['text'])

        if re.search('추천', request.form['text']):
            r = '뭘 추천해달라는거고 미친놈아'
        elif re.search('테스트', request.form['text']):
            r = '테스트 하지마라 새끼야'
        elif re.match('^yelp\s+(\S+)\s+(.*)$', request.form['text']):
            # this is fucking ugly
            m = re.match('^yelp\s+(\S+)\s+(.*)$', request.form['text'])
            term, location = m.group(1), m.group(2)

            # check_token()
            name,url,review_count,rating = yelpbot(term, location)
            r = name + ' ' + url.split('?')[0] + ' ' + str(review_count) + '\n' + str(rating)
        else:
            r = test()

        text = '{{"text":"{}"}}'.format(r)
        resp = Response(response=text, status=200, mimetype="application/json")
        return resp
    else:
        return 'ok'

def test():
    return '어쩌라고'

def dotenv():
    with open('.env', 'r') as f:
        for line in f.readlines():
            secrets = line.rstrip().split(':')
    return tuple(secrets)

#def check_token(token=None):
#    if token == 0:
#        token, expires_in, token_type = get_token()
#        start_time = int(time.time())
#    else:
#        if start_time + valid_for < int(time.time()):
#            token, expires_in, token_type = get_token()
#            start_time = int(time.time())
#

def get_token():
    yelp_id, yelp_secret = dotenv()
    res = requests.post('https://api.yelp.com/oauth2/token',
        data={'client_id': yelp_id, 'client_secret': yelp_secret})
    token = json.loads(res.text)
    return token['access_token'], token['expires_in'], token['token_type']

def yelpbot(term, location):
    token = 'nDC6jYxMccgjQo9Jesq8S-zyhaMiwhwaZoEI-lqzBh6t0NFc0mQjBCiJjrh_9Wj836U6BHAE2NSx2UnF-9Vnm0xUDCrVgzu_X7YoDXw63g1ppzDD0KWsTFIqhkEBWXYx'
    res = requests.get('https://api.yelp.com/v3/businesses/search?term={}&location={}'.format(term, location), headers={'Authorization':'Bearer {}'.format(token)})

    data = json.loads(res.text)

    Restaurant = namedtuple('Restaurant', 'name, url, review_count, rating')
    # 이렇게 namedtuple 의 청사진을 정의해 놓고 나중에 Restaurant 클래스 쓰듯이 r = Restaurant(a, b, c, d, e) 이렇게 사용
    # r.name OR r.location 이렇게 표현.

    must_try = [restaurant for restaurant in data['businesses'] if restaurant['rating'] > 3.4 and restaurant['review_count'] > 300]

    if len(must_try) > 0:
        must_try.sort(key=lambda r: r['review_count'], reverse=True)
        app.logger.info(must_try[0])
        '''
        {
            'coordinates': {'longitude': -121.995439343154, 'latitude': 37.382495134431},
            'categories': [{'title': 'American (Traditional)', 'alias': 'tradamerican'}, {'title': 'Burgers', 'alias': 'burgers'}, {'title': 'Sports Bars', 'alias': 'sportsbars'}],
            'display_phone': '(408) 738-8515',
            'is_closed': False,
            'location': {'address2': 'Ste 110', 'address3': '', 'city': 'Sunnyvale', 'zip_code': '94085', 'display_address': ['510 Lawrence Expy', 'Ste 110', 'Sunnyvale, CA 94085'], 'address1': '510 Lawrence Expy', 'country': 'US', 'state': 'CA'},
            'id': 'st-johns-bar-and-grill-sunnyvale-2',
            'review_count': 1944,
            'phone': '+14087388515',
            'transactions': [],
            'name': "St. John's Bar & Grill",
            'image_url': 'https://s3-media1.fl.yelpcdn.com/bphoto/yc2i37ilxxS6am6Gbdpqzw/o.jpg',
            'rating': 4.0, 'distance': 2734.1896414059997,
            'url': 'https://www.yelp.com/biz/st-johns-bar-and-grill-sunnyvale-2?adjust_creative=0-LllWs1Yqig2LM8S38itQ&utm_campaign=yelp_api_v3&utm_medium=api_v3_business_search&utm_source=0-LllWs1Yqig2LM8S38itQ',
            'price': '$$'
        }
        '''
        restaurants = [Restaurant(res['name'], res['url'], res['review_count'], res['rating']) for res in must_try]
        return (restaurants[0].name, restaurants[0].url, restaurants[0].review_count, restaurants[0].rating)
    else:
        return 'No search result!'



if __name__ == '__main__':
    handler = RotatingFileHandler('logs/alfred.log', maxBytes=10000, backupCount=1)
    handler.setLevel(logging.INFO)
    app.logger.setLevel(logging.INFO)
    app.logger.addHandler(handler)
    app.run(host='0.0.0.0', port=5005)


