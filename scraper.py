import requests
from bs4 import BeautifulSoup
from collections import namedtuple


def search_endic(search_term):
    url = 'http://m.endic.naver.com/search.nhn?searchOption=all&query=' + str(search_term)
    soup = BeautifulSoup(requests.get(url).text, 'html.parser')
    meanings = soup.select('div > div.word_wrap > ul > li')
    return "\n".join([m.p.text for m in meanings])


def exchange_rate():
    url = 'https://m.search.naver.com/search.naver?query=%ED%99%98%EC%9C%A8&where=m&sm=mtp_hty'
    soup = BeautifulSoup(requests.get(url).text, 'html.parser')
    exchange_rates = soup.select('div.exchange_table._html_table > table > tbody > tr')
    #ExchangeRate = namedtuple('ExchangeRate', 'country, rate, a_fluc, p_fluc')
    country, unit, kr_rate, actual_fluc, pct_fluc = ([rate.text.split() for rate in exchange_rates][0])
    return "{}: {} 원  {} ({})".format(unit, kr_rate, actual_fluc, pct_fluc)


if __name__ == '__main__':
    print(exchange_rate())
