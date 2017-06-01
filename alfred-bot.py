import os
import re
import random
import time

from slackclient import SlackClient
import requests

from scraper import exchange_rate, search_endic
from yelp_bot import YelpBot
#from dotenv import Dotenv

# starterbot's ID as an environment variable
BOT_ID = os.environ.get("BOT_ID")

# constants
AT_BOT = "<@" + BOT_ID + ">"
EXAMPLE_COMMAND = "do"
#ENGLISH = re.compile(r'^e\s+(.*)$')
#YELP = re.compile(r'^yelp\s+(.*)\s+(near|in)\s+(.*)$')

# instantiate Slack & Twilio clients
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))


def handle_command(command, channel):
    """
        Receives commands directed at the bot and determines if they
        are valid commands. If so, then acts on the commands. If not,
        returns back what it needs for clarification.
    """
    response = "Not sure what you mean. Use the *" + EXAMPLE_COMMAND + \
               "* command with numbers, delimited by spaces."
    if command.startswith(EXAMPLE_COMMAND):
        response = "Sure...write some more code then I can do that!"
    elif command.startswith('help'):
        response = alfred_help()
    elif command.startswith('실검'):
        response = real_time_search_queries()
    elif command.startswith('환율'):
        response = exchange_rate()
    else:
        response = random_resp()

    slack_client.api_call("chat.postMessage", channel=channel, text=response, as_user=True)
'''
    elif YELP.search(request.form['text']):
        m = YELP.search(request.form['text'])
        term, location = m.group(1), m.group(3)
        try:
            ybot = YelpBot()
            ybot.check_token_validity()
            r = ybot.call_search_api(term, location)
        except Exception as e:
            response = '*Sorry YelpBot couldn\'t process your request:* {} '.format(type(e)) + str(e)
'''


def parse_slack_output(slack_rtm_output):
    """
        The Slack Real Time Messaging API is an events firehose.
        this parsing function returns None unless a message is
        directed at the Bot, based on its ID.
    """
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:
            if output and 'text' in output and AT_BOT in output['text']:
                # return text after the @ mention, whitespace removed
                return output['text'].split(AT_BOT)[1].strip().lower(), \
                       output['channel']
    return None, None




def alfred_help():
    return 'e [영어단어] : 네이버 사전에서 영어 단어 검색\nyelp [음식종류] near [도시/위치] : 옐프 top 3 레스>토랑 검색\n 실검 : 네이버 현재 실시간 상위 검색어들'

def random_resp():
    r = ['어쩌라고', '하루 8시간 자라', '오락 그만해라', '책 좀 읽어라', '운동 좀 해라']
    return random.choice(r)

def real_time_search_queries():
    queries = re.findall('<span class="ah_k">(.*)</span>', requests.get('http://naver.com').text)[:20]
    return "[ *현재 네이버 실시간 검색 순위* ]\n" + "\n".join(queries)


if __name__ == "__main__":
    READ_WEBSOCKET_DELAY = 1 # 1 second delay between reading from firehose
    if slack_client.rtm_connect():
        print("Alfred is ready to serve you!")
        while True:
            command, channel = parse_slack_output(slack_client.rtm_read())
            if command and channel:
                handle_command(command, channel)
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")
