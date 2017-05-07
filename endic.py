import requests
from bs4 import BeautifulSoup


def search_endic(search_term):
    url = 'http://m.endic.naver.com/search.nhn?searchOption=all&query=' + str(search_term)
    soup = BeautifulSoup(requests.get(url).text, 'html.parser')
    meanings = soup.select('div > div.word_wrap > ul > li')
    return "\n".join([m.p.text for m in meanings])

