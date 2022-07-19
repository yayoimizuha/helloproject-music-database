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

df = pandas.read_excel(os.path.join(os.getcwd(), 'merged.xlsx'), sheet_name='Sheet1', index_col=0)
print('rows:', df.__len__())
print(df.iloc[1])


def get_itunes_info(row):
    url, artist_name, release_name, release_type, release_date, record_label, song_name, length, lyrics, composition, arrangement = row.tolist()
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
        return [{'collectionName': 'None'},
                [None, 'None', None, 'http://cdn.helloproject.com/img/release/o/nowprinting.jpg', None, 'None'],
                row.tolist()]

    return response


i = 6000


def increment():
    global i
    print(i, end='->')
    i += 1
    print(i)
    if i >= df.__len__():
        i = df.__len__() - 1
    global info
    info = get_itunes_info(df.iloc[i])
    artist_label['text'] = info[1][1]
    album_label['text'] = info[0]['collectionName']
    song_label['text'] = info[1][5]

    global canvas
    global img
    img = PIL.ImageTk.PhotoImage(
        PIL.Image.open(io.BytesIO(requests.get(info[1][3].replace('5000x5000', '1000x1000')).content)))
    canvas.itemconfig(tagOrId='image', image=img)

    print(info)


def decrement():
    global i
    print(i, end='->')
    i -= 1
    print(i)
    if i < 0:
        i = 0
    global info
    info = get_itunes_info(df.iloc[i])

    artist_label['text'] = info[1][1]
    album_label['text'] = info[0]['collectionName']
    song_label['text'] = info[1][5]

    global canvas
    global img
    img = PIL.ImageTk.PhotoImage(
        PIL.Image.open(io.BytesIO(requests.get(info[1][3].replace('5000x5000', '1000x1000')).content)))
    canvas.itemconfig(tagOrId='image', image=img)

    print(info)


root = Tk()
root.geometry('2000x1100+100+100')
root.title('H!P Release & iTunes Connector')

info = get_itunes_info(df.iloc[4000])
artist_label = tkinter.Label(root, text=info[1][1], font=("", 20))
artist_label.place(x=20, y=20)

album_label = tkinter.Label(root, text=info[0]['collectionName'], font=("", 20))
album_label.place(x=20, y=60)

song_label = tkinter.Label(root, text=info[1][5], font=("", 20))
song_label.place(x=20, y=100)

artwork = PIL.ImageTk.PhotoImage(
    PIL.Image.open(io.BytesIO(requests.get(info[1][3].replace('5000x5000', '500x500')).content)))
canvas = tkinter.Canvas(root, width=1000, height=1000)
canvas.place(x=700, y=0)
canvas.create_image(
    0,
    0,
    image=artwork,
    anchor=tkinter.NW,
    tag='image'
)

decBtn = tkinter.Button(text='前へ', command=lambda: decrement())
decBtn.place(x=20, y=140)
incBtn = tkinter.Button(text='次へ', command=lambda: increment())
incBtn.place(x=20, y=180)


def slideshow():
    increment()
    global root
    root.after(300, slideshow)


root.after(300, slideshow)
root.mainloop()
