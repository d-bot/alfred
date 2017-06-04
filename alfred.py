import logging
from logging.handlers import RotatingFileHandler
import random
import re

import requests
from flask import Flask, request, Response

from cache_token import CacheToken
from scraper import exchange_rate, search_endic
from yelp_bot import YelpBot

RECOMMEND = re.compile('추천')
RT_SEARCH = re.compile('실검')
TEST = re.compile('테스트')
ENGLISH = re.compile(r'^eng\s+(.*)$')
HELP = re.compile('help')
EXCHANGE_RATE = re.compile('환율')
YELP = re.compile(r'^yelp\s+(.*)\s+(near|in)\s+(.*)$')

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def alfred():

    if request.form['user_id'] != 'USLACKBOT':
        if RECOMMEND.search(request.form['text']):
            r = '뭘 추천해달라는거고 미친놈아'
        elif TEST.search(request.form['text']):
            r = '테스트 하지마라 새끼야'
        elif RT_SEARCH.search(request.form['text']):
            r = real_time_search_queries()
        elif EXCHANGE_RATE.search(request.form['text']):
            r = exchange_rate()
        elif ENGLISH.search(request.form['text']):
            m = ENGLISH.search(request.form['text'])
            r = search_endic(m.group(1))
        elif HELP.search(request.form['text']):
            r = alfred_help()
        elif YELP.search(request.form['text']):
            m = YELP.search(request.form['text'])
            term, location = m.group(1), m.group(3)
            try:
                ybot = YelpBot()
                ybot.check_token_validity()
                r = ybot.call_search_api(term, location)
            except Exception as e:
                r = '*Sorry YelpBot couldn\'t process your request:* {} '.format(type(e)) + str(e)
        else:
            r = None

        if r is not None:
            #text = '{{"text":"{}"}}'.format(r)
            #text = formatter(r)
            resp = Response(response=r, status=200, mimetype="application/json")
            return resp
        else:
            return 'ok'
    else:
        return 'ok'

#def random_resp():
#    r = ['어쩌라고', '하루 8시간 자라', '오락 그만해라', '책 좀 읽어라', '운동 좀 해라']
#    return random.choice(r)


def alfred_help():
    return '''{
    "attachments": [
        {
            "pretext": "이렇게 사용해주세요.",
            "title": "HELP",
            "fields": [
                {
                    "title": "eng [영어단어]",
                    "value": "네이버 사전에서 영어 단어 검색",
                    "short": true
                },
                {
                    "title": "yelp [음식종류] near [도시/위치]",
                    "value": "옐프 top 3 레스토랑 검색",
                    "short": true
                },
                {
                    "title": "실검",
                    "value": "현재 네이버 실시간 상위 검색어들",
                    "short": true
                },
                {
                    "title": "환율",
                    "value": "현재 U.S 달러 환율",
                    "short": true
                }
            ],
            "color": "#F35A00"
        }
    ]
    }'''

def real_time_search_queries():
    queries = re.findall('<span class="ah_k">(.*)</span>', requests.get('http://naver.com').text)[:20]
    output = "\n".join(queries)
    return '''{
    "attachments": [
        {
            "title": "%s",
            "text": "%s",
            "color": "#36a64f"
        }
    ]
    }''' % ('현재 네이버 실시간 검색 순위', output)






if __name__ == '__main__':
    handler = RotatingFileHandler('logs/alfred.log', maxBytes=100000000, backupCount=1)
    handler.setLevel(logging.INFO)
    app.logger.setLevel(logging.INFO)
    app.logger.addHandler(handler)
    app.run(host='0.0.0.0', port=5007, debug=True)
    #app.run(host='0.0.0.0', port=5007)

