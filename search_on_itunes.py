import datetime
import random
import re
import sys
import difflib
import time
import requests
import urllib, urllib.parse
import joblib
import json
import pprint
import mojimoji
import unicodedata


def safe_request_get_as_text(url):
    err_num = 0
    get_error = 0
    text = ""
    while get_error == 0:
        try:
            page = requests.get(url)
            text = page.text
            if page.status_code == 404:
                return None
            if page.status_code == 301:
                time.sleep(5)
            get_error += 1
        except BaseException as error:
            print("\n\n\n" + "Error occurred:(1) " + str(error) + "\n\n\n")
            sys.stderr.flush()
            sys.stdout.flush()
            err_num += 1
        if err_num > 5:
            continue

    return unicodedata.normalize('NFKC', text)


def search_on_itunes(search_keyword, artist_keyword=""):
    original_keyword = search_keyword
    search_keyword = unicodedata.normalize('NFKC', search_keyword)
    artist_keyword = unicodedata.normalize('NFKC', artist_keyword)
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
    result_json = safe_request_get_as_text(
        "https://itunes.apple.com/search?term=" + search_keyword +
        "&media=music&entity=song&attribute=songTerm&country=jp&lang=ja_jp&limit=50&GenreTerm=J-Pop&sort=recent")
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
    print("番号\tアーティスト名\tトラック名\t収録アルバム名\tゲシュタルトパターンマッチングによる類似率(低いほど良い)\tiTunesのURL")

    result_list = []
    for i in range(len(result_json)):
        flag = 0
        print(i + 1, end='\t')
        normalized_track_name = unicodedata.normalize('NFKC', result_json[i]["trackName"])
        normalized_collection_name = unicodedata.normalize('NFKC', result_json[i]["collectionName"])
        normalized_artist_name = unicodedata.normalize('NFKC', result_json[i]["artistName"])
        normalized_artist_name = re.sub(r'\(.*\)', '', normalized_artist_name)

        print(normalized_artist_name, end='\t')
        print(normalized_track_name, end='\t')
        print(normalized_collection_name, end='\t')

        normalized_collection_name = normalized_collection_name.replace("EP", "")
        gestalt_track_distance = difflib.SequenceMatcher(None, normalized_track_name, search_keyword).ratio()
        gestalt_collection_distance = difflib.SequenceMatcher(None, normalized_track_name,
                                                              normalized_collection_name).ratio()
        gestalt_artist_distance = difflib.SequenceMatcher(None, artist_keyword, normalized_artist_name).ratio()
        print('{:.4f}'.format(gestalt_artist_distance), end='\t')
        print('{:.4f}'.format(gestalt_track_distance), end='\t')
        print('{:.4f}'.format(gestalt_collection_distance), end='\t')

        if "releaseDate" not in result_json[i]:
            print('')
            continue
        elif int(result_json[i]["releaseDate"][0:4]) < 1983:
            print('')
            continue

        release_date = datetime.datetime.fromisoformat(result_json[i]["releaseDate"][0:-1]).timestamp()
        date_distance = (time.time() - release_date) / (60 * 60 * 24 * 365 * 40)
        print('{:.4f}'.format(date_distance), end='\t')
        sort_index = gestalt_track_distance * gestalt_artist_distance + gestalt_collection_distance * 1 + date_distance
        print('{:.5f}'.format(sort_index), end='\t')
        print(datetime.datetime.fromtimestamp(release_date).strftime('%Y年%m月%d日'), end='\t')

        print(result_json[i]["collectionViewUrl"], end='\t')

        if "Instrumental" in result_json[i]["trackName"]:
            print('')
            continue

        album_json = json.loads(safe_request_get_as_text(
            "https://itunes.apple.com/lookup?country=jp&lang=ja_jp&id=" + str(result_json[i]["collectionId"])))

        if album_json["resultCount"] == 0:
            print('')
            continue

        # if "プッチベスト" in result_json[i]["collectionName"] or "プッチベスト" in result_json[i]["collectionName"]:
        #     print('')
        #     continue

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

        result_list.append([result_json[i]["trackId"], i, -sort_index])
        print("\n\t 👆Use at search.")

    if len(result_list) == 0:
        print("\n\nヒット件数: 0\t該当するデータが見つかりませんでした。")
        sys.exit()

    print("\n\nヒット件数: %d" % len(result_list))

    random.shuffle(result_list)
    result = sorted(result_list, key=lambda x: x[2])[0][1]
    result = result_json[result]

    print("\n\nトラック情報:")
    # result = json.loads(unicodedata.normalize('NFKC', json.dumps(result, ensure_ascii=False)))
    print(json.dumps(result, indent=4, ensure_ascii=False))

    print("\n\n収録アルバム情報:")
    album_json = json.loads(safe_request_get_as_text(
        "https://itunes.apple.com/lookup?country=jp&lang=ja_jp&id=" + str(result["collectionId"])))["results"][0]
    # album_json = unicodedata.normalize('NFKC', album_json)
    print(json.dumps(album_json, indent=4, ensure_ascii=False))

    print('\n\n')
    print("収録アルバム: " + result["collectionName"])
    print("楽曲名: " + result["trackName"])
    print("アーティスト名: " + result["artistName"])
    print("iTunesのページ: " + result["collectionViewUrl"])
    print("アートワークのURL: " + result["artworkUrl100"].replace("100x100bb", "5000x5000bb"))
    print("検索: https://www.google.com/search?q=" + urllib.parse.quote(result["trackName"]))

    print('\n\n')
    artist_json = requests.get(
        "https://itunes.apple.com/lookup?country=jp&lang=ja_jp&id=" + str(result["artistId"])).text
    print(json.dumps(json.loads(artist_json)["results"][0], indent=4, ensure_ascii=False))

    return [result["collectionName"], result["collectionId"],
            result["trackName"], result["trackId"],
            result["artistName"], result["artistId"],
            result["collectionViewUrl"],
            result["artworkUrl100"].replace("100x100bb", "5000x5000bb"),
            "https://www.google.com/search?q=" + urllib.parse.quote(result["trackName"]),
            result, album_json]

# pprint.pprint(search_on_itunes(search_keyword="氷点下"))
