# http://www.up-front-works.jp/release/
import pprint
from search_on_itunes import safe_request_get_as_text
from bs4 import BeautifulSoup
import requests

release_page_url = "http://www.up-front-works.jp/release/search/?g=single&-s=1"

page_text = requests.get(release_page_url).text

pprint.pprint(page_text)

page_obj = BeautifulSoup(page_text, 'html.parser')
release_list = page_obj.find('div', {'id': 'release_list'})
pprint.pprint(release_list, indent=4)
print(len(release_list))
