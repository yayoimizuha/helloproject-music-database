# http://www.up-front-works.jp/release/
import html
import pprint
from search_on_itunes import safe_request_get_as_text
from bs4 import BeautifulSoup
import requests

release_url = "http://www.up-front-works.jp/release/search/?-s=1&g=single&p=10"

header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:97.0) Gecko/20100101 Firefox/97.0'
}


# def safe_request_get_as_text(url, header):
#     return requests.get(url).text


def road_release_list(release_page_url):
    page_text = safe_request_get_as_text(release_page_url, header=header)

    # pprint.pprint(page_text)

    page_obj = BeautifulSoup(page_text, 'html.parser')

    release_list = page_obj.find('div', {'id': 'release_list'}).find_all('a', {'class', 'box'})

    return_list = []
    artist = ""
    for i in range(len(release_list)):
        artist = release_list[i].find('img')['alt']
        print(artist)
        print('http://www.up-front-works.jp' + release_list[i]['href'] + '\n')
        return_list.append([release_list[i]['href'], artist])
    # pprint.pprint(release_list)
    return return_list


def road_release_page(url):
    return_table = []
    release_info = safe_request_get_as_text(url[0], header=header)
    release_info_obj = BeautifulSoup(release_info, 'html.parser').find('div', {'id': 'right'}).find_all('table')
    # print(html.unescape(release_info_obj.prettify()))
    for j in range(len(release_info_obj)):
        if 'CD' not in release_info_obj[j].find_previous().text:
            continue
        # print(html.unescape(release_info_obj[j].prettify()))
        # print('\n\n\n\n\n\n\n\n\n\n')
        # print('http://www.up-front-works.jp' + i + '\t' + str(j))
        return_table.append(release_info_obj[j])
    return return_table


# road_table(road_release_page(road_release_list(release_url)))

release_list_urls = ["http://www.up-front-works.jp/release/search/?-s=1&g=single&p=1"]

for release_list_url in release_list_urls:
    release_list_items = road_release_list(release_list_url)

    for release_list_item in release_list_items:
        release_list_item = ['http://www.up-front-works.jp' + release_list_item[0], release_list_item[1]]
        release_page_tables = road_release_page(release_list_item)

        for release_page_table in release_page_tables:

            for column in release_page_table.find_all('tr'):
                if not column.has_attr('class'):
                    if column.find('p') is None:
                        pass
                        # continue
                    else:
                        if column.find('p').has_attr('class') is False:
                            pass
                        # continue
                        else:
                            if column.find('p')['class'][0] == 'no_songs':
                                continue
                    if column.find('td')['class'][0] == 'hide_cell':
                        continue
                    # print(column.find('p').has_attr('class'))

                    print("-----------------------------------------------")
                    print(column.find('td', {'class': 'columnA'}).text + '\t' +
                          column.find('td', {'class': 'columnB'}).text + '\t' +
                          column.find('td', {'class': 'columnC'}).text + '\t' +
                          column.find('td', {'class': 'columnD'}).text + '\t' +
                          column.find('td', {'class': 'columnE'}).text + '\t' +
                          column.find('td', {'class': 'columnF'}).text)
                    print(release_list_item[1].split(':')[0])
