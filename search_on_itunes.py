import datetime
import math
import random
import re
import sys
import requests
import urllib, urllib.parse
import joblib
import json
import pprint
import mojimoji

search_keyword = "大きな愛でもてなして"
search_keyword = search_keyword.replace(',', '、')
search_keyword = search_keyword.replace('&', '＆')
search_keyword = search_keyword.replace('!', '！')
if search_keyword[-1:].isdigit() or search_keyword[-1:].isascii():
    search_keyword += " "
if search_keyword[0].isdigit() or search_keyword[0].isascii():
    search_keyword = ' ' + search_keyword
search_keyword = mojimoji.zen_to_han(search_keyword, ascii=False, kana=False)
# search_keyword = re.sub(r'([0-9]+)', ',\1,', search_keyword)
# print('"' + search_keyword + '"')
# search_keyword = urllib.parse.quote(search_keyword)
# search_keyword = "恋愛レボリューション21 "
print('"' + search_keyword + '"')
result_json = requests.get(
    "https://itunes.apple.com/search?term=" + search_keyword +
    "&media=music&entity=song&attribute=songTerm&country=jp&lang=ja_jp&limit=200").text
result_json = json.loads(result_json)
result_json = result_json["results"]
# pprint.pprint(result_json[0])

if len(result_json) == 0:
    sys.exit()

result_list = []
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
    print("最初のリリース: " + datetime.datetime.isoformat(datetime.datetime.fromtimestamp(first_release)) + "\n\n")

print("検索結果: " + str(len(result_json)), end='\t\t')
print("番号\tアーティスト名\tトラック名\tトラックID\t収録アルバム名\t収録アルバムID\tリリース日\tiTunesのURL")

for i in range(len(result_json)):
    print(i + 1, end='\t')
    print(result_json[i]["artistName"], end='\t')
    print(result_json[i]["trackName"], end='\t')
    print(result_json[i]["trackId"], end='\t')
    print(result_json[i]["collectionName"], end='\t')
    print(result_json[i]["collectionId"], end='\t')
    if "releaseDate" not in result_json[i]:
        print('')
        continue
    print(result_json[i]["releaseDate"], end='\t')
    print(result_json[i]["collectionViewUrl"], end='\t')

    if result_json[i]["primaryGenreName"] != "J-Pop":
        # print('\n different Genre name')
        print('')
        continue
    album_json = json.loads(requests.get("https://itunes.apple.com/lookup?country=jp&lang=ja_jp&id=" +
                                         str(result_json[i]["collectionId"])).text)
    if album_json["resultCount"] == 0:
        # print('\n None album result.')
        print('')
        continue
    if datetime.datetime.fromisoformat(album_json["results"][0]["releaseDate"][0:-1]) \
            - datetime.datetime.fromtimestamp(first_release) > datetime.timedelta(days=31):
        continue
        # print('\n too far from release')
        # continue
    if result_json[i]["isStreamable"] is True:
        # print('\n Streamable')
        print('')
        continue

    result_list.append([result_json[i]["trackId"], i])
    print("\n\t 👆Use at search.")

if result_list is None:
    sys.exit()
# random.shuffle(result_list)
result = sorted(result_list, key=lambda x: x[0])[0][1]
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

# print('\n\n')
# pprint.pprint(json.loads(
#     requests.get("https://itunes.apple.com/lookup?country=jp&lang=ja_jp&id=" + str(result["artistId"])).text)[
#                   "results"][0])
