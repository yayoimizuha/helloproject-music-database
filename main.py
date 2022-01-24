import os
import pprint
import sys

import search_on_youtube
from contextlib import redirect_stdout

result = search_on_youtube.search_on_youtube(search_keyword="ポップミュージック", artist_keyword='KAN',
                                             api_key='AIzaSyC4rd76PUGRfPZlcS9q-28VB1nV34mZv4Y', use_itunes_search=True)

pprint.pprint(result, indent=4)

sys.exit()

with redirect_stdout(open(os.devnull, 'w', encoding='utf-8-sig')):
    result = search_on_youtube.search_on_youtube(search_keyword='ポップミュージック', artist_keyword='KAN',
                                                 api_key='AIzaSyC4rd76PUGRfPZlcS9q-28VB1nV34mZv4Y',
                                                 use_itunes_search=True)

pprint.pprint(result, indent=4)
