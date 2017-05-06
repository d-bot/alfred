import logging
from logging.handlers import RotatingFileHandler
import random
import re
import json
import time
from collections import namedtuple

import requests

from flask import Flask, request, Response
from cache_token import CacheToken

app = Flask(__name__)

y_token, expire_in = CacheToken().get_token()
expire_at = expire_in + int(time.time())

@app.route('/', methods=['GET', 'POST'])
def alfred():
    if expire_at < int(time.time()):
        app.logger.info('Token has expired. Requesting new token')
    #    y_token, expire_in = CacheToken().get_token()
    #    app.logger.info('Received a new token: {} and it will expire in {}'.format(y_token, expire_in))
    #else:
    #    app.logger.info('Time left: {}'.format(expire_at-int(time.time())))


    if request.form['user_id'] != 'USLACKBOT':
        if re.search('추천', request.form['text']):
            r = '뭘 추천해달라는거고 미친놈아'
        elif re.search('테스트', request.form['text']):
            r = '테스트 하지마라 새끼야'
        elif re.search('실검', request.form['text']):
            r = real_time_search_queries()
        elif re.search('yelp', request.form['text']):
            m = re.match('^yelp\s+(.*)\s+(near|in)\s+(.*)$', request.form['text'])
            term, location = m.group(1), m.group(3)
            try:
                r = yelpbot(term, location)
            except Exception as e:
                r = '*Sorry Yelp-bot couldn\'t process your request:* {} '.format(type(e)) + str(e)
        else:
            r = test()

        text = '{{"text":"{}"}}'.format(r)
        resp = Response(response=text, status=200, mimetype="application/json")
        return resp
    else:
        return 'ok'

def test():
    r = ['어쩌라고', '하루 8시간 자라', '오락 그만해라', '책 좀 읽어라', '운동 좀 해라']
    return random.choice(r)

def real_time_search_queries():
    queries = re.findall('<span class="ah_k">(.*)</span>', requests.get('http://naver.com').text)[:20]
    return "[ *현재 네이버 실시간 검색 순위* ]\n" + "\n".join(queries)

def check_token_validity():
    if expire_at < int(time.time()):
        app.logger.info('Token has expired. Requesting new token')
        #y_token, expire_in = CacheToken().get_token()  # this makes problematic!!!!
        app.logger.info('Received a new token: {} and it will expire in {}'.format(y_token, expire_in))
    #else:
        #app.logger.info('current token looks ok: {}'.format(y_token))


def yelpbot(term, location):
    check_token_validity()
    res = requests.get('https://api.yelp.com/v3/businesses/search?term={}&location={}'.format(term, location), headers={'Authorization':'Bearer {}'.format(y_token)})
    data = json.loads(res.text)
    Restaurant = namedtuple('Restaurant', 'name, url, review_count, rating')
    must_try = [restaurant for restaurant in data['businesses'] if restaurant['rating'] > 3.4 and restaurant['review_count'] > 300]

    if len(must_try) > 0:
        must_try.sort(key=lambda r: r['review_count'], reverse=True)
        restaurants = [Restaurant(res['name'], res['url'], res['review_count'], res['rating'])
                for res in must_try][:3]

        res_output = ''
        for res in restaurants:
            res_output = res_output + " *[ {} ]*\n{}\nReview Count: {}\nRating: {}\n\n".format(res.name, res.url.split('?')[0], res.review_count, res.rating)

        return res_output

    else:
        return 'No search result!'


if __name__ == '__main__':
    handler = RotatingFileHandler('logs/alfred.log', maxBytes=100000000, backupCount=1)
    handler.setLevel(logging.INFO)
    app.logger.setLevel(logging.INFO)
    app.logger.addHandler(handler)
    app.run(host='0.0.0.0', port=5005, debug=True)



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
