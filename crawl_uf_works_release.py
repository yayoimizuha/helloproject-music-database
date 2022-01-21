import json
import os
import pprint
from collections import OrderedDict
import search_on_itunes
from googleapiclient.discovery import build

youtube = build(
    "youtube",
    "v3",
    developerKey=os.environ['API_KEY']
)

itunes_search = search_on_itunes.search_on_itunes(search_keyword="初恋サイダー", artist_keyword="Buono!")

youtube_search_responce = youtube.search().list(q=itunes_search[4] + ' ' + itunes_search[2], part='id,snippet',
                                                maxResults=25).execute()

print('\n\n')

# print(json.dumps(youtube_search_responce, indent=4, ensure_ascii=False))

search_result = youtube_search_responce["items"]
print(len(search_result))

print("\n\n")
for i in range(len(search_result)):
    print(i)
    print(json.dumps(search_result[i]["snippet"]["channelId"], indent=4, ensure_ascii=False))
    if search_result[i]["id"]["kind"] != "youtube#video":
        continue
    response = youtube.videos().list(part='contentDetails', id=search_result[i]["id"]["videoId"]).execute()
    if response["items"][0]["contentDetails"]["licensedContent"] is True:
        print(json.dumps(response, indent=4, ensure_ascii=False))
