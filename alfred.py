import logging
from logging.handlers import RotatingFileHandler
import random
import re

import requests
from flask import Flask, request, Response

from cache_token import CacheToken
from scraper import exchange_rate, search_endic, real_time_search_queries, alfred_help
from yelp_bot import YelpBot
from household import run_household

RT_SEARCH = re.compile('실검')
ENGLISH = re.compile(r'^eng\s+(.*)$')
HELP = re.compile('help')
EXCHANGE_RATE = re.compile('환율')
YELP = re.compile(r'^yelp\s+(.*)\s+(near|in)\s+(.*)$')

actions = ( (RT_SEARCH, real_time_search_queries), (ENGLISH, search_endic), (HELP, alfred_help), (EXCHANGE_RATE, exchange_rate), (YELP, None) )

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def alfred():

    if request.form['user_id'] != 'USLACKBOT':
        for cond,action in actions:
            m = cond.search(request.form['text'])
            if m is not None:
                if len(m.groups()) == 0:
                    r = action()
                elif len(m.groups()) == 1:
                    r = action(m.group(1))
                elif len(m.groups()) == 3:
                    term, location = m.group(1), m.group(3)
                    try:
                        ybot = YelpBot()
                        ybot.check_token_validity()
                        r = ybot.call_search_api(term, location)
                    except Exception as ex:
                        r = '*Sorry YelpBot couldn\'t process your request:* {} '.format(type(e)) + str(e)
                else:
                    print('I do not understand regex match result: '.format(len(m.groups())))
                break

            elif m is None:
                r = None

        if r is not None:
            resp = Response(response=r, status=200, mimetype="application/json")
            return resp
        else:
            return 'ok'

    else:
        return 'ok'


@app.route('/household', methods=['GET'])
def check_household():
    r = run_household()
    resp = Response(response=r, status=200, mimetype="application/json")
    return resp


if __name__ == '__main__':
    handler = RotatingFileHandler('logs/alfred.log', maxBytes=100000000, backupCount=1)
    handler.setLevel(logging.INFO)
    app.logger.setLevel(logging.INFO)
    app.logger.addHandler(handler)
    #app.run(host='0.0.0.0', port=5007, debug=True)
    app.run(host='0.0.0.0', port=5007)

