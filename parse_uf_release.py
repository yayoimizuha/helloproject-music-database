# http://www.up-front-works.jp/release/
import html
import pprint
from search_on_itunes import safe_request_get_as_text
from bs4 import BeautifulSoup
import requests

release_page_url = "http://www.up-front-works.jp/release/search/?g=single&-s=1"

header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:97.0) Gecko/20100101 Firefox/97.0'
}

page_text = safe_request_get_as_text(release_page_url, header=header)

# pprint.pprint(page_text)

page_obj = BeautifulSoup(page_text, 'html.parser')

release_list = page_obj.find('div', {'id': 'release_list'}).find_all('a', {'class', 'box'})

for i in range(len(release_list)):
    print(release_list[i].find('img')['alt'])
    print('http://www.up-front-works.jp' + release_list[i]['href'])
    release_info = safe_request_get_as_text('http://www.up-front-works.jp' + release_list[i]['href'], header=header)
    release_info_obj = BeautifulSoup(release_info, 'html.parser').find('div', {'id': 'right'}).find_all('table')
    # print(html.unescape(release_info_obj.prettify()))
    for j in range(len(release_info_obj)):
        if 'CD' not in release_info_obj[j].find_previous().text:
            continue
        print(html.unescape(release_info_obj[j].find_previous().text))
        print(str(i) + '\t' + str(j))

pprint.pprint(release_list)
