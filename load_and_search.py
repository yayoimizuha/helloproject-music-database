import datetime
import os.path
import pprint
import time

from search_on_itunes import search_on_itunes_v2
import pandas

pandas.options.display.max_rows = None
pandas.options.display.max_columns = None
pandas.options.display.width = 6000
pandas.options.display.max_colwidth = 6000
pandas.options.display.colheader_justify = 'left'

df = pandas.read_excel(os.path.join(os.getcwd(), 'merged.xlsx'), sheet_name='Sheet1', index_col=0)

for _, col in df.iterrows():
    url, artist_name, release_name, release_type, release_date, record_label, song_name, length, lyrics, composition, arrangement = col
    print(artist_name)
    print(release_name)
    print(song_name)
    print(int(str(length).split(':')[0]) * 60 + int(str(length).split(':')[1]))
    print(datetime.datetime.strptime(release_date, '%Y/%m/%d').date())
    print('\n\n\n')
    response = search_on_itunes_v2(artist_name=artist_name, album_name=release_name, song_name=song_name,
                                   released_date=datetime.datetime.strptime(release_date, '%Y/%m/%d').date(),
                                   length=int(str(length).split(':')[0]) * 60 + int(str(length).split(':')[1]),
                                   debug=False)
    pprint.pprint(response)
    # time.sleep(1)

    # time.sleep(0.3)

    # search_result = search_on_itunes(search_keyword=song_name, artist_keyword=artist_name, debug=True)
    # # pprint.pprint(search_result)
    # album_name, _, itunes_song_name, _, itunes_artist_name, _, itunes_page, artwork_url, google_link, json_data, album_json = search_result
    # print(album_name)
    # print(itunes_song_name)
    # print(itunes_artist_name)
    # print(itunes_page)
    # print(artwork_url)
    # print('\n\n\n\n\n')
