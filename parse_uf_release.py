# http://www.up-front-works.jp/release/
import pprint
from search_on_itunes import safe_request_get_as_text
from bs4 import BeautifulSoup
import requests

release_page_url = "http://www.up-front-works.jp/release/"

page_text = requests.get(release_page_url).text

pprint.pprint(page_text)
