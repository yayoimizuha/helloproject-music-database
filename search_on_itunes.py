import random
import re
import sys
import requests
import urllib, urllib.parse
import joblib
import json
import pprint
import mojimoji

search_keyword = "46億年LOVE"
search_keyword = search_keyword.replace(',', '、')
search_keyword = search_keyword.replace('&', '＆')
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
    "&media=music&entity=song&attribute=songTerm&country=jp&lang=ja_jp").text
result_json = json.loads(result_json)
result_json = result_json["results"]
# pprint.pprint(result_json[0])

print(len(result_json), end='\t')
print("アーティスト名\tトラック名\tトラックID\t収録アルバム名\t収録アルバムID\tリリース日\tiTunesのURL")

if len(result_json) == 0:
    sys.exit()

result_list = []
for i in range(len(result_json)):
    if "releaseDate" not in result_json[i]:
        continue
    print(i, end='\t')
    print(result_json[i]["artistName"], end='\t')
    print(result_json[i]["trackName"], end='\t')
    print(result_json[i]["trackId"], end='\t')
    print(result_json[i]["collectionName"], end='\t')
    print(result_json[i]["collectionId"], end='\t')
    print(result_json[i]["releaseDate"], end='\t')
    print(result_json[i]["collectionViewUrl"])

    result_list.append([result_json[i]["trackId"], i])

# random.shuffle(result_list)
result = sorted(result_list, key=lambda x: x[0])[0][1]
result = result_json[result]

print('\n\n\n\n')

pprint.pprint(result)
print('\n\n\n\n')
print("収録アルバム: " + result["collectionName"])
print("楽曲名: " + result["trackName"])
print("iTunesページ: " + result["collectionViewUrl"])
print("アートワークのURL: " + result["artworkUrl100"].replace("100x100bb", "5000x5000bb"))
