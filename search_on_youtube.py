import datetime
import json
import os
import pprint
import time
import unicodedata

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

    # youtube_official_movies = [['0Lo7k25-5PI',
    #                             '2234351',
    #                             324405827.7490101,
    #                             'ハロー！プロジェクト モベキマス 『ブスにならない哲学』 '
    #                             '(MV)'],
    #                            ['QuvZHjnJcPg',
    #                             '1229641',
    #                             319933925.8114283,
    #                             'ハロー！プロジェクト モベキマス 『ブスにならない哲学』 '
    #                             '(Group Lip Ver.)']]
    pprint.pprint(youtube_official_movies, indent=4)

    youtube_movies_sorter = []
    for i in range(len(youtube_official_movies)):
        youtube_movies_sorter.append(
            [-round(int(youtube_official_movies[i][1]) * youtube_official_movies[i][2] * 10e-14, 10), i])

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
