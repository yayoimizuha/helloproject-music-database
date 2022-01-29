# http://www.up-front-works.jp/release/
import datetime
import html
import pprint
import re
import sys
import sqlite3
from search_on_itunes import safe_request_get_as_text
from bs4 import BeautifulSoup
import requests
import pandas

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


# release_list_page_urls = ["http://www.up-front-works.jp/release/search/?-s=1&g=single&p=36"]
def process_release_info(release_list_urls):
    release_music_list = []
    for release_list_url in release_list_urls:
        release_list_items = road_release_list(release_list_url)

        for release_list_item in release_list_items:
            release_list_item = ['http://www.up-front-works.jp' + release_list_item[0], release_list_item[1]]
            release_page_tables = road_release_page(release_list_item)

            for release_page_table in release_page_tables:
                print("**************************************************")

                print(release_list_item[0])
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

                        print("---------------------")
                        print(release_list_item[1].rsplit(':', 1)[0])
                        print(column.find('td', {'class': 'columnA'}).text + '\t' +
                              column.find('td', {'class': 'columnB'}).text + '\t' +
                              column.find('td', {'class': 'columnC'}).text + '\t' +
                              column.find('td', {'class': 'columnD'}).text + '\t' +
                              column.find('td', {'class': 'columnE'}).text + '\t' +
                              column.find('td', {'class': 'columnF'}).text)

                        song_name = column.find('td', {'class': 'columnB'}).contents[0]

                        # if all(map(song_name.__contains__, ("2018アコースティックVer.", "Lover", "LOVER", "every", "Every"))):
                        if re.search(r'2018アコースティックVer.|Lover|LOVER|every|Every', song_name,
                                     flags=re.IGNORECASE) is not None:
                            re_text = r'(ボーカル|Inst|feat|カラオケ|テーマ|live|ライブ|mix|take|Al|edit|バージョン|ば〜じょん|' \
                                      r'ヴァージョン|主題歌|ソング|ニング|リミックス|accoustic|ボ-カル|duet|とともに|より|video|' \
                                      r'updated|スマイレージ)'

                        else:
                            re_text = r'(ボーカル|Inst|feat|ver|カラオケ|テーマ|live|ライブ|mix|take|Al|edit|バージョン|ば〜じょん' \
                                      r'|ヴァージョン|主題歌|ソング|ニング|リミックス|accoustic|ボ-カル|duet|とともに|より|video|' \
                                      r'updated|スマイレージ)'

                        song_name = re.sub(r'[<](.*?)' + re_text + r'(.*?)[>]', '', song_name, flags=re.IGNORECASE)
                        song_name = re.sub(r'[(](.*?)' + re_text + r'(.*?)[)]', '', song_name, flags=re.IGNORECASE)
                        song_name = re.sub(r'[~](.*?)' + re_text + r'(.*?)[~]', '', song_name, flags=re.IGNORECASE)
                        song_name = re.sub(r'[～](.*?)' + re_text + r'(.*?)[～]', '', song_name, flags=re.IGNORECASE)
                        song_name = re.sub(r'[〜](.*?)' + re_text + r'(.*?)[〜]', '', song_name, flags=re.IGNORECASE)

                        song_name = re.sub(r'^\(.*?(Instrumental|feat|ver|カラオケ).*', '', song_name, flags=re.IGNORECASE)
                        song_name = re.sub(r'【|Additional Track|enhanced|】', '', song_name)
                        song_name = re.sub(r'※.*', '', song_name)

                        # print(song_name)
                        release_music_list.append([release_list_item[1].rsplit(':', 1)[0],
                                                   release_list_item[1].rsplit(':', 1)[1].replace('\t', ''),
                                                   song_name,
                                                   release_list_item[0]])
    return release_music_list


def save_dataframe(data_list, release_type):
    dataframe = pandas.DataFrame(data_list, columns=['artist', 'collectionName', 'trackName', 'release_page'])
    pandas.options.display.max_rows = None
    pandas.options.display.max_columns = None
    pandas.options.display.width = 6000
    pandas.options.display.max_colwidth = 6000

    print("\nduplicated values:\n" + str(dataframe.duplicated().value_counts()))

    dataframe = dataframe.drop_duplicates()

    print(dataframe)

    sqlite_connect = sqlite3.connect(str(datetime.date.today()) + '_dropped_duplicate.sqlite')
    dataframe.to_sql(release_type, sqlite_connect, if_exists='replace')
    sqlite_connect.close()


release_list_page_urls = []

for page_num in range(39):
    print("http://www.up-front-works.jp/release/search/?-s=1&g=single&p=" + str(page_num + 1))
    release_list_page_urls.append("http://www.up-front-works.jp/release/search/?-s=1&g=single&p=" + str(page_num + 1))

save_dataframe(process_release_info(release_list_page_urls), 'single')

release_list_page_urls = []

for page_num in range(24):
    print("http://www.up-front-works.jp/release/search/?-s=1&g=album&&p=" + str(page_num + 1))
    release_list_page_urls.append("http://www.up-front-works.jp/release/search/?-s=1&g=album&&p=" + str(page_num + 1))

save_dataframe(process_release_info(release_list_page_urls), 'album')

# pprint.pprint(release_music_list)

# print(dataframe)
# dataframe.to_excel(str(datetime.date.today()) + '.xlsx')


# dataframe.to_excel(str(datetime.date.today()) + '_dropped_duplicate.xlsx')
