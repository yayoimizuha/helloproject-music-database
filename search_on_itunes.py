import random
import re
import requests
import urllib, urllib.parse
import joblib
import json
import pprint

search_keyword = "泳げないMermaid"
search_keyword = urllib.parse.quote(re.sub(r"[0-9]", ',', search_keyword))
# print(search_keyword)
result_json = requests.get(
    "https://itunes.apple.com/search?term=" + search_keyword +
    "&media=music&entity=song&attribute=songTerm&country=jp&lang=ja_jp").text
result_json = json.loads(result_json)
result_json = result_json["results"]
# pprint.pprint(result_json[0])

# print(len(result_json))

result_list = []
for i in range(len(result_json)):
    # print(i, end=' ')
    # print(result_json[i]["artistName"], end='\t')
    # print(result_json[i]["collectionViewUrl"], end='\t')
    # print(result_json[i]["trackName"], end='\t')
    # print(result_json[i]["trackId"])
    # print(result_json[i]["collectionName"])
    result_list.append([result_json[i]["trackId"], i])

random.shuffle(result_list)
result = sorted(result_list, key=lambda x: x[0])[0][1]
result = result_json[result]
pprint.pprint(result)
print(result["collectionName"])
print(result["trackName"])

