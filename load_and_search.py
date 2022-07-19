import datetime
import io
import os.path
import pprint
import time
import tkinter
from tkinter import *
from tkinter import ttk

import PIL.ImageTk
import PIL.Image
import requests

from search_on_itunes import search_on_itunes_v2
import pandas

pandas.options.display.max_rows = None
pandas.options.display.max_columns = None
pandas.options.display.width = 6000
pandas.options.display.max_colwidth = 6000
pandas.options.display.colheader_justify = 'left'

# root = Tk()
# root.geometry('1600x600')
# root.title('H!P Release & iTunes Connector')
# artist_label = tkinter.Label(root, text="artist", font=("", 20))
# artist_label.place(x=20, y=20)
# album_label = tkinter.Label(root, text="album", font=("", 20))
# album_label.place(x=20, y=60)
# song_label = tkinter.Label(root, text="song", font=("", 20))
# song_label.place(x=20, y=100)
#
# artwork = PIL.ImageTk.PhotoImage(
#     PIL.Image.open(io.BytesIO(requests.get('http://cdn.helloproject.com/img/release/o/nowprinting.jpg').content)))
# canvas = tkinter.Canvas(root, width=500, height=500)
# canvas.place(x=1000, y=0)
# canvas.create_image(
#     0,
#     0,
#     image=artwork,
#     anchor=tkinter.NW
# )

df = pandas.read_excel(os.path.join(os.getcwd(), 'merged.xlsx'), sheet_name='Sheet1', index_col=0)

for _, col in df.iterrows():
    url, artist_name, release_name, release_type, release_date, record_label, song_name, length, lyrics, composition, arrangement = col.tolist()
    print('\n\n\n')
    print(artist_name)
    print(release_name)
    print(song_name)
    print(int(str(length).split(':')[0]) * 60 + int(str(length).split(':')[1]))
    print(datetime.datetime.strptime(release_date, '%Y/%m/%d').date())
    response = search_on_itunes_v2(artist_name=artist_name, album_name=release_name, song_name=song_name,
                                   released_date=datetime.datetime.strptime(release_date, '%Y/%m/%d').date(),
                                   length=int(str(length).split(':')[0]) * 60 + int(str(length).split(':')[1]),
                                   debug=False)

    if response == [None, None, 0]:
        print("Not found!")
        continue

    pprint.pprint(response[1])

    root = Tk()
    root.geometry('1600x600+100+100')
    root.title('H!P Release & iTunes Connector')

    artist_label = tkinter.Label(root, text=response[1][1], font=("", 20))
    artist_label.place(x=20, y=20)

    album_label = tkinter.Label(root, text=response[0]['collectionName'], font=("", 20))
    album_label.place(x=20, y=60)

    song_label = tkinter.Label(root, text=response[1][5], font=("", 20))
    song_label.place(x=20, y=100)

    artwork = PIL.ImageTk.PhotoImage(
        PIL.Image.open(io.BytesIO(requests.get(response[1][3].replace('5000x5000', '500x500')).content)))
    canvas = tkinter.Canvas(root, width=500, height=500)
    canvas.place(x=1000, y=0)
    canvas.create_image(
        0,
        0,
        image=artwork,
        anchor=tkinter.NW
    )

    root.mainloop()
    # time.sleep(5)
    # time.sleep(10)
    # input()

    time.sleep(1)

    # search_result = search_on_itunes(search_keyword=song_name, artist_keyword=artist_name, debug=True)
    # # pprint.pprint(search_result)
    # album_name, _, itunes_song_name, _, itunes_artist_name, _, itunes_page, artwork_url, google_link, json_data, album_json = search_result
    # print(album_name)
    # print(itunes_song_name)
    # print(itunes_artist_name)
    # print(itunes_page)
    # print(artwork_url)
    # print('\n\n\n\n\n')
