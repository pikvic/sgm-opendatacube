from urllib.parse import urlparse
import requests
from pystac import STAC_IO
from pystac import Catalog

def requests_read_method(uri):
    parsed = urlparse(uri)
    print(parsed)
    if parsed.scheme.startswith('http'):
        return requests.get(uri).text
    else:
        return STAC_IO.default_read_text_method(uri)

def stac_test():
    path, row = '010', '117'
    url = f'https://landsat-stac.s3.amazonaws.com/landsat-8-l1/{path}/{row}/catalog.json'
    cat = Catalog.from_file(url)

    #for item in cat.get_items():
    #    print(item.id)
    return True

STAC_IO.read_text_method = requests_read_method