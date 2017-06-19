from cache_token import CacheToken
import requests
import time
import json
from collections import namedtuple


class YelpBot:
    def __init__(self):
        self.y_token, self.expire_in = CacheToken().get_token()
        self.expire_at = self.expire_in + int(time.time())

    def check_token_validity(self):
        if self.expire_at < int(time.time()):
            # How do I want to get logger object here? I'll think about it later for now...
            #app.logger.info('Token has expired. Requesting new token')
            self.y_token, self.expire_in = CacheToken().get_token()
            #app.logger.info('Received a new token: {} and it will expire in {}'.format(self.y_token, expire_in))
        #else:
            #app.logger.info('current token looks ok: {}'.format(self.y_token))


    def call_search_api(self, term, location):
        res = requests.get('https://api.yelp.com/v3/businesses/search?term={}&location={}'.format(term, location), headers={'Authorization':'Bearer {}'.format(self.y_token)})
        data = json.loads(res.text)
        Restaurant = namedtuple('Restaurant', 'name, url, review_count, rating')
        must_try = [restaurant for restaurant in data['businesses'] if restaurant['rating'] > 3.4 and restaurant['review_count'] > 300]

        if len(must_try) > 0:
            must_try.sort(key=lambda r: r['review_count'], reverse=True)
            restaurants = [Restaurant(res['name'], res['url'], res['review_count'], res['rating']) for res in must_try][:3]
            res_output = ''
            for res in restaurants:
                res_output = res_output + " *[ {} ]*\n{}\nReview Count: {}\nRating: {}\n\n".format(res.name, res.url.split('?')[0], res.review_count, res.rating)

            return '''{
    "attachments": [
        {
            "pretext": "Top 3 yelp search result",
            "fallback": "API Error- Yelp API not working: https://api.yelp.com/v3/",
            "title": "Top 3 Search Result",
            "title_link": "https://www.yelp.com/",
            "text": "...",
            "fields": [
                {
                    "title": "%s",
                    "value": "%s\nReview Count: %s",
                    "short": false
                },
                {
                    "title": "%s",
                    "value": "%s\nReview Count: %s",
                    "short": false
                },
                {
                    "title": "%s",
                    "value": "%s\nReview Count: %s",
                    "short": false
                }
            ],
            "color": "#C7111B"
        }
    ]
}''' % (restaurants[0].name, restaurants[0].url.split('?')[0], restaurants[0].review_count, restaurants[1].name, restaurants[1].url.split('?')[0], restaurants[1].review_count, restaurants[2].name, restaurants[2].url.split('?')[0], restaurants[2].review_count)

        else:
            return 'No search result!'

if __name__ == '__main__':
    ybot = YelpBot()
    ybot.check_token_validity()
    print(ybot.call_search_api('burrito', 'santa clara'))
