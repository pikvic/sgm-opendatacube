from urllib.parse import urlparse
import requests
from pystac import STAC_IO, Catalog


def requests_read_method(uri):
    parsed = urlparse(uri)
    if parsed.scheme.startswith('http'):
        return requests.get(uri).text
    else:
        return STAC_IO.default_read_text_method(uri)


def get(path, row):
    url = f"https://landsat-stac.s3.amazonaws.com/landsat-8-l1/{path:03d}/{row:03d}/catalog.json"
    cat = Catalog.from_file('https://landsat-stac.s3.amazonaws.com/catalog.json')
    item = next(cat.get_children())
    for item in item.get_children():
        print(item)

if __name__ == "__main__":
    STAC_IO.read_text_method = requests_read_method
    get(17, 110)