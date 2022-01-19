import random
import re
import requests
import urllib, urllib.parse
import joblib
import json
import pprint

search_keyword = "恋愛レボリューション21 "
print(urllib.parse.quote(search_keyword, safe=''))
search_keyword = urllib.parse.quote(search_keyword, safe='')
print(search_keyword)
result_json = requests.get(
    "https://itunes.apple.com/search?term=" + search_keyword +
    "&media=music&entity=song&attribute=songTerm&country=jp&lang=ja_jp").text
result_json = json.loads(result_json)
result_json = result_json["results"]
# pprint.pprint(result_json[0])

print(len(result_json))

result_list = []
for i in range(len(result_json)):
    if result_json[i]["isStreamable"] is True:
        pass
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
print("アートワークのURL: " + result["artworkUrl100"].replace("100x100bb", "2000x2000bb"))
