import datetime
import difflib
import html
import json
import os
import pprint
import re
import time
import unicodedata

import Levenshtein

import search_on_itunes
from googleapiclient.discovery import build

API_KEY = os.getenv('API_KEY', default='')


def search_on_youtube(search_keyword, artist_keyword='', use_itunes_search=False, api_key=API_KEY):
    if api_key == '':
        print("No API Key.")
        return []
    youtube = build(
        "youtube",
        "v3",
        developerKey=api_key
    )

    if use_itunes_search is True:
        itunes_search = search_on_itunes.search_on_itunes(search_keyword=search_keyword, artist_keyword=artist_keyword)
        search_keyword = itunes_search[2]
        artist_keyword = itunes_search[4]
    else:
        itunes_search = []
    youtube_search_result = youtube.search().list(q='"' + artist_keyword + '" "' + search_keyword + '"',
                                                  part='id,snippet',
                                                  fields='items(id(videoId,kind),snippet(title,publishTime))',
                                                  maxResults=4).execute()
    youtube_search_result = json.loads(
        unicodedata.normalize('NFKC', json.dumps(youtube_search_result, ensure_ascii=False)))

    print('\n\n')
    print(json.dumps(youtube_search_result, indent=4, ensure_ascii=False))
    search_result = json.loads(json.dumps(youtube_search_result["items"], ensure_ascii=False))
    print(len(search_result))

    print("\n\n")

    youtube_official_movies = []

    for i in range(len(search_result)):
        # print(i)
        # print(json.dumps(search_result[i]["snippet"]["channelId"], indent=4, ensure_ascii=False))
        if search_result[i]["id"]["kind"] != "youtube#video":
            continue

        video_info = youtube.videos().list(part='contentDetails,statistics,snippet',
                                           fields='items(contentDetails/licensedContent,statistics/viewCount,'
                                                  'snippet/channelId)',
                                           id=search_result[i]["id"]["videoId"]).execute()
        video_info = json.loads(unicodedata.normalize('NFKC', json.dumps(video_info, ensure_ascii=False)))

        if video_info["items"][0]["contentDetails"]["licensedContent"] is True:
            print("https://youtu.be/" + search_result[i]["id"]["videoId"])
            print(video_info["items"][0]["statistics"]["viewCount"] + "回")
            print(search_result[i]["snippet"]["publishTime"])
            print(search_result[i]["snippet"]["title"])
            print(json.dumps(video_info, indent=4, ensure_ascii=False))
            print('')

            youtube_official_movies.append(["https://youtu.be/" + search_result[i]["id"]["videoId"],
                                            video_info["items"][0]["statistics"]["viewCount"],
                                            time.time()
                                            - datetime.datetime.fromisoformat(search_result[i]["snippet"]["publishTime"]
                                                                              .replace('Z', '+00:00')).timestamp(),
                                            search_result[i]["snippet"]["title"],
                                            video_info["items"][0]["snippet"]["channelId"]])

    # youtube_official_movies = [['https://youtu.be/O4Bl0ehLQic',
    #                             '849759',
    #                             63033286.33872008,
    #                             'KAN『ポップミュージック』 Short Version',
    #                             'UCB-MAg09TKnDv7shND16ghg'],
    #                            ['https://youtu.be/IrggLg_hGE0',
    #                             '3919620',
    #                             59559282.48766899,
    #                             'Juice=Juice『ポップミュージック』(Juice=Juice [Pop Music])(Promotion Edit)',
    #                             'UC6FadPgGviUcq6VQ0CEJqdQ']]
    pprint.pprint(youtube_official_movies, indent=4)

    movie_regex_one = r"[\(（]([a-zA-Z\s\[\]\'\"”””“\.…,\/　!！=。’℃・\-])*[\)）]"
    movie_regex_two = r"Promotion Edit"
    movie_regex_three = r"[\[\(（]([a-zA-Z\s”\[［\]］\.\/’\'&。”“0-9\?!×#~,（）])*[\]\)）]"
    movie_regex_four = r"ショート|Short|short|Version|Ver.|Ver|バージョン|Dance|ダンス|リリック|"
    youtube_movies_sorter = []
    for i in range(len(youtube_official_movies)):
        movie_name = html.unescape(youtube_official_movies[i][3])
        movie_name = re.sub(movie_regex_one, '', movie_name)
        movie_name = re.sub(movie_regex_two, '', movie_name)
        movie_name = re.sub(movie_regex_three, '', movie_name)
        movie_name = re.sub(movie_regex_four, "", movie_name)
        print(movie_name)
        movie_name_diff = Levenshtein.distance(movie_name, artist_keyword + ' ' + search_keyword)
        print(str(movie_name_diff) + "\n\n\n\n")
        youtube_movies_sorter.append(
            [-round(int(youtube_official_movies[i][1]) * youtube_official_movies[i][2] * 10e-14 / movie_name_diff, 10),
             i])

    pprint.pprint(youtube_movies_sorter)
    if len(youtube_movies_sorter) == 0:
        return [itunes_search, []]
    youtube_movie = sorted(youtube_movies_sorter, key=lambda x: x[0])[0][1]
    print(youtube_official_movies[youtube_movie][4])
    channel = youtube.channels().list(part='snippet', fields='items(snippet/title)',
                                      id=youtube_official_movies[youtube_movie][4]).execute()

    channel = json.loads(unicodedata.normalize('NFKC', json.dumps(channel, ensure_ascii=False)))

    youtube_official_movies[youtube_movie].append(channel["items"][0]["snippet"]["title"])

    return [itunes_search, youtube_official_movies[youtube_movie]]

# youtube_search = search_on_youtube(search_keyword="がんばれないよ", artist_keyword="Juice=Juice")
# pprint.pprint(youtube_search)
