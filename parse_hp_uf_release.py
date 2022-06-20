import pprint
import pandas
from bs4 import BeautifulSoup
from search_on_itunes import safe_request_get_as_text
from urllib import parse

pandas.options.display.max_rows = None
pandas.options.display.max_columns = None
pandas.options.display.width = 6000
pandas.options.display.max_colwidth = 6000
pandas.options.display.colheader_justify = 'left'

request_header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'ja',
    'Accept-Encoding': 'gzip, deflate',
    'Prefer': 'safe',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1'
}

# single_release_url_base = 'http://www.helloproject.com/release/search/?-s=1&g=single&p='
# album_release_url_base = 'http://www.helloproject.com/release/search/?-s=1&g=album&p='
# distribution_release_url_base = 'http://www.helloproject.com/release/search/?-s=1&g=distribution&p='

uf_single_release_url_base = 'http://www.up-front-works.jp/release/search/?-s=1&g=single&p='
uf_album_release_url_base = 'http://www.up-front-works.jp/release/search/?-s=1&g=album&p='
uf_distribution_release_url_base = 'http://www.up-front-works.jp/release/search/?-s=1&g=distribution&p='

dataframe = pandas.DataFrame(
    columns=['url', 'artist_name', 'release_name', 'release_type', 'release_date',
             'record_label', 'song_name',
             'length', 'lyrics', 'composition', 'arrangement'])
print(dataframe)
df_index = 0


def crawl(base_url):
    page_range = 1
    while True:
        page = BeautifulSoup(safe_request_get_as_text(base_url + str(page_range), header=request_header), 'html.parser')
        contents = page.find('div', {'id': 'release_list'}).find_all('a', {'class': 'box'})
        # pprint.pprint(contents)
        if not len(contents):
            break

        for content in contents:
            scheme = parse.urlparse(base_url).scheme + '://'
            hostname = parse.urlparse(base_url).hostname
            print(scheme + hostname + content['href'])
            process_page(scheme + hostname + content['href'])
            print()
        page_range += 1


def process_page(page_url):
    global dataframe
    global df_index
    page = BeautifulSoup(safe_request_get_as_text(page_url), 'html.parser')
    if page.find('a', {'class': 'modal'})['href'] == \
            'nowprinting.jpg':
        return 0
    content = page.find('div', {'id': 'right'})
    release_name = content.find('h2', {'class': 'product_title'}).contents[0].text
    print(release_name)
    artist_name = content.find('h3', {'class': 'artist'}).text
    release_type = content.find('table', {'class': 'data1'}).find_all('td', {'class': 'columnB'})[0].text
    release_date = content.find('table', {'class': 'data1'}).find_all('td', {'class': 'columnB'})[1].text
    record_label = content.find('table', {'class': 'data1'}).find_all('td', {'class': 'columnB'})[2].text
    print('\t' + release_name)
    print('\t' + artist_name)
    print('\t' + release_type)
    print('\t' + release_date)
    print('\t' + record_label)
    if not content.find('p', {'class', 'no_songs'}) is None:
        return 0
    print('\t盤数: ' + str(len(content.find_all('h3', {'class': 'notes'}))))
    for tables in content.find_all('table', {'class': 'data2'}):
        if 'CD' in tables.find_previous('h4').text or '配信' in tables.find_previous('h4').text:
            print('\t\t' + tables.find_previous('h4').text)
        else:
            continue
        music_list = tables.find_all('tr')[1:]

        for list_col in music_list:
            if list_col.find('td', {'class': 'hide_cell'}):
                continue
            data = [page_url, artist_name, release_name, release_type, release_date, record_label,
                    list_col.find('td', {'class': 'columnB'}).text,
                    list_col.find('td', {'class': 'columnC'}).text,
                    list_col.find('td', {'class': 'columnD'}).text,
                    list_col.find('td', {'class': 'columnE'}).text,
                    list_col.find('td', {'class': 'columnF'}).text]
            escaped_data = []
            [escaped_data.append(s.replace('\r', '').replace('\t', '').replace('\n', '')) for s in data]
            pprint.pprint(escaped_data, width=1000)
            dataframe.loc[df_index] = escaped_data
            df_index += 1


crawl(uf_single_release_url_base)
print()
crawl(uf_album_release_url_base)
print()
crawl(uf_distribution_release_url_base)
print()

dataframe.sort_values('release_date', inplace=True)
print('別verを削除: ' +
      str(len(dataframe[dataframe['song_name'].str.contains(r'【.*?】')].index)
          + len(dataframe[dataframe['song_name'].str.contains(r'\(*?inst|ver|mix.*?\)', case=False)].index)))

dataframe = dataframe[dataframe['song_name'].str.contains(r'【.*?】') == False]
dataframe = dataframe[dataframe['song_name'].str.contains(r'\(*?inst|ver|mix.*?\)', case=False) == False]

dataframe.drop_duplicates(subset=['song_name', 'release_name', 'artist_name'], inplace=True)
dataframe.reset_index(drop=True, inplace=True)

dataframe.to_excel('uf.xlsx')
