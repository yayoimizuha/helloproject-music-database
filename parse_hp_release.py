import pprint
import pandas
from bs4 import BeautifulSoup
from search_on_itunes import safe_request_get_as_text

pandas.options.display.max_rows = None
pandas.options.display.max_columns = None
pandas.options.display.width = 6000
pandas.options.display.max_colwidth = 6000
pandas.options.display.colheader_justify = 'left'

single_release_url_base = 'http://www.helloproject.com/release/search/?-s=1&g=single&p='
album_release_url_base = 'http://www.helloproject.com/release/search/?-s=1&g=album&p='
distribution_release_url_base = 'http://www.helloproject.com/release/search/?-s=1&g=distribution&p='

dataframe = pandas.DataFrame(
    columns=['url', 'artist_name', 'release_name', 'release_type', 'release_date',
             'record_label', 'song_name',
             'length', 'lyrics', 'composition', 'arrangement'])
print(dataframe)
df_index = 0


def crawl(base_url):
    page_range = 1
    while True:
        page = BeautifulSoup(safe_request_get_as_text(base_url + str(page_range)), 'html.parser')
        contents = page.find_all('section')
        if not len(contents):
            break

        for content in contents:
            print('http://www.helloproject.com' + content.find('a')['href'])
            process_page('http://www.helloproject.com' + content.find('a')['href'])
            print()
        page_range += 1


def process_page(page_url):
    global dataframe
    global df_index
    page = BeautifulSoup(safe_request_get_as_text(page_url), 'html.parser')
    if page.find('li', {'class': 'thumb_m'}).find('a')['href'] == \
            'http://cdn.helloproject.com/img/release/o/nowprinting.jpg':
        return 0
    content = page.find('div', {'id': 'rd_right'})
    release_name = content.find_all('h2')[0].text
    artist_name = content.find('p', {'id': 'artist_name'}).text
    release_type = content.find('div', {'id': 'table_wrapper'}).find_all('td', {'class': 'item02'})[0].text
    release_date = content.find('div', {'id': 'table_wrapper'}).find_all('td', {'class': 'item02'})[1].text
    record_label = content.find('div', {'id': 'table_wrapper'}).find_all('td', {'class': 'item02'})[2].text
    print('\t' + release_name, end='')
    print('\t' + artist_name)
    print('\t' + release_type)
    print('\t' + release_date)
    print('\t' + record_label)

    print('\t板数: ' + str(len(content.find_all('div', {'class': 'release_edition'}))))
    for tables in content.find_all('table', {'class': 'typeB'}):
        if 'CD' in tables.find('th', {'colspan': '7'}).text or '配信' in tables.find('th', {'colspan': '7'}).text:
            print('\t\t' + tables.find('th', {'colspan': '7'}).text)
        else:
            continue
        music_list = tables.find_all('tr')[2:]
        for list_col in music_list:
            if list_col.find('td', {'class': 'hide_cell'}):
                continue
            data = [page_url, artist_name, release_name, release_type, release_date, record_label,
                    list_col.find('td', {'class': 'item02'}).text,
                    list_col.find('td', {'class': 'item03'}).text,
                    list_col.find('td', {'class': 'item04'}).text,
                    list_col.find('td', {'class': 'item05'}).text,
                    list_col.find('td', {'class': 'item06'}).text]
            escaped_data = []
            [escaped_data.append(s.replace('\r', '').replace('\t', '').replace('\n', '')) for s in data]
            pprint.pprint(escaped_data, width=1000)
            dataframe.loc[df_index] = escaped_data
            df_index += 1


crawl(single_release_url_base)
print()
crawl(album_release_url_base)
print()
crawl(distribution_release_url_base)

dataframe.sort_values('release_date', inplace=True)
print('別verを削除: ' +
      str(len(dataframe[dataframe['song_name'].str.contains(r'【.*?】')].index)
          + len(dataframe[dataframe['song_name'].str.contains(r'\(*?inst|ver|mix.*?\)', case=False)].index)))

dataframe = dataframe[dataframe['song_name'].str.contains(r'【.*?】') == False]
dataframe = dataframe[dataframe['song_name'].str.contains(r'\(*?inst|ver|mix.*?\)', case=False) == False]

dataframe.drop_duplicates(subset=['song_name', 'artist_name'], inplace=True)
dataframe.reset_index(drop=True, inplace=True)

dataframe.to_excel('test.xlsx')
