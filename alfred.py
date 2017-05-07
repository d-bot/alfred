import logging
from logging.handlers import RotatingFileHandler
import random
import re

import requests
from flask import Flask, request, Response

from cache_token import CacheToken
from endic import search_endic
from yelp_bot import YelpBot

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def alfred():

    if request.form['user_id'] != 'USLACKBOT':
        if re.search('추천', request.form['text']):
            r = '뭘 추천해달라는거고 미친놈아'
        elif re.search('테스트', request.form['text']):
            r = '테스트 하지마라 새끼야'
        elif re.search('실검', request.form['text']):
            r = real_time_search_queries()
        elif re.search('^e\s+', request.form['text']):
            m = re.match('^e\s+(.*)$', request.form['text'])
            r = search_endic(m.group(1))
        elif re.search('^help', request.form['text']):
            r = alfred_help()
        elif re.search('y\s+', request.form['text']):
            m = re.match('^y\s+(.*)\s+(near|in)\s+(.*)$', request.form['text'])
            term, location = m.group(1), m.group(3)
            try:
                ybot = YelpBot()
                ybot.check_token_validity()
                r = ybot.call_search_api(term, location)
            except Exception as e:
                r = '*Sorry YelpBot couldn\'t process your request:* {} '.format(type(e)) + str(e)
        else:
            r = random_resp()

        text = '{{"text":"{}"}}'.format(r)
        resp = Response(response=text, status=200, mimetype="application/json")
        return resp
    else:
        return 'ok'

def random_resp():
    r = ['어쩌라고', '하루 8시간 자라', '오락 그만해라', '책 좀 읽어라', '운동 좀 해라']
    return random.choice(r)

def alfred_help():
    return 'e [영어단어] : 네이버 사전에서 영어 단어 검색\nyelp [음식종류] near [도시/위치] : 옐프 top 3 레스토랑 검색\n 실검 : 네이버 현재 실시간 상위 검색어들'

def real_time_search_queries():
    queries = re.findall('<span class="ah_k">(.*)</span>', requests.get('http://naver.com').text)[:20]
    return "[ *현재 네이버 실시간 검색 순위* ]\n" + "\n".join(queries)


if __name__ == '__main__':
    handler = RotatingFileHandler('logs/alfred.log', maxBytes=100000000, backupCount=1)
    handler.setLevel(logging.INFO)
    app.logger.setLevel(logging.INFO)
    app.logger.addHandler(handler)
    app.run(host='0.0.0.0', port=5007, debug=True)

