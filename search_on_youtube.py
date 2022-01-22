import json
import os
import pprint
import search_on_itunes
from googleapiclient.discovery import build

youtube = build(
    "youtube",
    "v3",
    developerKey=os.environ['API_KEY']
)

itunes_search = search_on_itunes.search_on_itunes(search_keyword="初恋サイダー", artist_keyword="Buono!")

youtube_search_result = youtube.search().list(q=itunes_search[4] + ' ' + itunes_search[2], part='id,snippet',
                                              maxResults=10).execute()

print('\n\n')

# print(json.dumps(youtube_search_result, indent=4, ensure_ascii=False))

search_result = json.loads(json.dumps(youtube_search_result["items"], ensure_ascii=False))
print(len(search_result))

print("\n\n")
for i in range(len(search_result)):
    # print(i)
    # print(json.dumps(search_result[i]["snippet"]["channelId"], indent=4, ensure_ascii=False))
    if search_result[i]["id"]["kind"] != "youtube#video":
        continue
    video_info = youtube.videos().list(part='contentDetails,statistics', id=search_result[i]["id"]["videoId"]).execute()
    if video_info["items"][0]["contentDetails"]["licensedContent"] is True:
        # print(json.dumps(video_info, indent=4, ensure_ascii=False))
        print("https://youtu.be/" + video_info["items"][0]["id"])
        print(video_info["items"][0]["statistics"]["viewCount"])
        print(search_result[i]["snippet"]["publishTime"])
        print(search_result[i]["snippet"]["title"])
        print('')
