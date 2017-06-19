import requests
from bs4 import BeautifulSoup
from collections import namedtuple


def search_endic(search_term):
    url = 'http://m.endic.naver.com/search.nhn?searchOption=all&query=' + str(search_term)
    soup = BeautifulSoup(requests.get(url).text, 'html.parser')
    meanings = soup.select('div > div.word_wrap > ul > li')
    output = "\n".join([m.p.text for m in meanings])
    return '''{
    "attachments": [
        {
            "fallback": "m.endic.naver.com/search.nhn",
            "title": "%s",
            "title_link": "%s",
            "text": "%s",
            "color": "#52D0DF"
        }
    ]
    }''' % (search_term, 'http://m.endic.naver.com/search.nhn?searchOption=all&query='+search_term, output)



def exchange_rate():
    url = 'https://m.search.naver.com/search.naver?query=%ED%99%98%EC%9C%A8&where=m&sm=mtp_hty'
    soup = BeautifulSoup(requests.get(url).text, 'html.parser')
    exchange_rates = soup.select('div.exchange_table._html_table > table > tbody > tr')
    #ExchangeRate = namedtuple('ExchangeRate', 'country, rate, a_fluc, p_fluc')
    country, unit, kr_rate, actual_fluc, pct_fluc = ([rate.text.split() for rate in exchange_rates][0])
    output = "{}: {} 원  {} ({})".format(unit, kr_rate, actual_fluc, pct_fluc)
    return '''{
    "attachments": [
        {
            "fallback": "http://m.exchange.daum.net/mobile/exchange/exchangeDetail.daum?code=USD",
            "title": "U.S 환율",
            "title_link": "http://m.exchange.daum.net/mobile/exchange/exchangeDetail.daum?code=USD",
            "text": "%s",
            "color": "#36a64f"
        }
    ]
    }''' % output


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


if __name__ == '__main__':
    print(exchange_rate())
