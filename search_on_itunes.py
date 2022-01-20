import datetime
import random
import re
import sys
import difflib
import requests
import urllib, urllib.parse
import joblib
import json
import pprint
import mojimoji
search_keyword = "Wonderful World"

original_keyword = search_keyword
search_keyword = search_keyword.replace(',', '、')
search_keyword = search_keyword.replace('&', '＆')
search_keyword = search_keyword.replace('!', '！')
search_keyword = search_keyword.replace('(', '（')
search_keyword = search_keyword.replace(')', '）')
search_keyword = search_keyword.replace(' ', '　')
if search_keyword[-1:].isdigit() or search_keyword[-1:].isascii():
    search_keyword += " "
if search_keyword[0].isdigit() or search_keyword[0].isascii():
    search_keyword = ' ' + search_keyword
search_keyword = mojimoji.zen_to_han(search_keyword, ascii=False, kana=False)

print('検索文字列: "' + search_keyword + '"')
result_json = requests.get(
    "https://itunes.apple.com/search?term=" + search_keyword +
    "&media=music&entity=song&attribute=songTerm&country=jp&lang=ja_jp&limit=200&GenreTerm=J-Pop&sort=recent").text
result_json = json.loads(result_json)
result_json = result_json["results"]

if len(result_json) == 0:
    sys.exit()

first_release = sys.float_info.max
for i in range(len(result_json)):
    if "releaseDate" not in result_json[i]:
        continue
    if int(result_json[i]["releaseDate"][0:4]) < 1995:
        continue
    if result_json[i]["isStreamable"] is True:
        continue
    if result_json[i]["primaryGenreName"] != "J-Pop":
        continue
    if datetime.datetime.fromisoformat(result_json[i]["releaseDate"][0:-1]).timestamp() < first_release:
        first_release = datetime.datetime.fromisoformat(result_json[i]["releaseDate"][0:-1]).timestamp()
if first_release is sys.float_info.max:
    print("検索結果: 0")
    sys.exit()
else:
    print("\n" + "最初のリリース: " + datetime.datetime.isoformat(datetime.datetime.fromtimestamp(first_release)) + "\n")

print("検索結果: " + str(len(result_json)))
print("番号\tアーティスト名\tトラック名\t収録アルバム名\tゲシュタルトパターンマッチングによる類似率\tiTunesのURL")

result_list = []
for i in range(len(result_json)):
    flag = 0
    print(i + 1, end='\t')

    print(result_json[i]["artistName"], end='\t')

    print(result_json[i]["trackName"], end='\t')

    print(result_json[i]["collectionName"], end='\t')

    gestalt_track_distance = difflib.SequenceMatcher(None, result_json[i]["trackName"], search_keyword).ratio()
    gestalt_collection_distance = difflib.SequenceMatcher(None, result_json[i]["trackName"],
                                                          result_json[i]["collectionName"]).ratio()
    print('{:.4f}'.format(gestalt_track_distance), end='\t')
    print('{:.4f}'.format(gestalt_collection_distance), end='\t')
    print('{:.5f}'.format(gestalt_track_distance * gestalt_collection_distance + gestalt_track_distance * 2), end='\t')

    print(result_json[i]["collectionViewUrl"], end='\t')

    if "releaseDate" not in result_json[i]:
        print('')
        continue

    album_json = json.loads(requests.get("https://itunes.apple.com/lookup?country=jp&lang=ja_jp&id=" +
                                         str(result_json[i]["collectionId"])).text)

    if album_json["resultCount"] == 0:
        print('')
        continue

    # if "プッチベスト" in result_json[i]["collectionName"] or "プッチベスト" in result_json[i]["collectionName"]:
    #     print('')
    #     continue

    if "Instrumental" in result_json[i]["trackName"]:
        print('')
        continue

    if "copyright" not in album_json["results"][0]:
        print('')
        continue
    if 'UP-FRONT' in album_json["results"][0]["copyright"]:
        pass
    elif 'PONY CANYON' in album_json["results"][0]["copyright"]:
        pass
    else:
        print('')
        continue

    if result_json[i]["trackTimeMillis"] < 120000:
        print('')
    release_date = datetime.datetime.fromisoformat(album_json["results"][0]["releaseDate"][0:-1]).timestamp()
    result_list.append([result_json[i]["trackId"], i,
                        -(gestalt_track_distance * gestalt_collection_distance + gestalt_track_distance * 2)])
    print("\n\t 👆Use at search.")

if result_list is None:
    sys.exit()

random.shuffle(result_list)
result = sorted(result_list, key=lambda x: x[2])[0][1]
result = result_json[result]

print("\n\nトラック情報:")
pprint.pprint(result)

print("\n\n収録アルバム情報:")
album_json = requests.get(
    "https://itunes.apple.com/lookup?country=jp&lang=ja_jp&id=" + str(result["collectionId"])).text
pprint.pprint(json.loads(album_json)["results"][0])

print('\n\n')
print("収録アルバム: " + result["collectionName"])
print("楽曲名: " + result["trackName"])
print("アーティスト名: " + result["artistName"])
print("iTunesのページ: " + result["collectionViewUrl"])
print("アートワークのURL: " + result["artworkUrl100"].replace("100x100bb", "5000x5000bb"))
print("検索: https://www.google.com/search?q=" + urllib.parse.quote(result["trackName"]))

print('\n\n')
artist_json = requests.get("https://itunes.apple.com/lookup?country=jp&lang=ja_jp&id=" + str(result["artistId"])).text
pprint.pprint(json.loads(artist_json)["results"][0])
