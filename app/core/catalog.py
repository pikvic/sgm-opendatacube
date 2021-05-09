import json
import httpx
import pprint
import asyncio
import datetime
import uuid
from helpers import ConvertToWRS
import datacube
from datacube.index.hl import Doc2Dataset

async def get_item(url):
    async with httpx.AsyncClient() as client:
        print(f"Getting item from {url}")
        response = await client.get(url)
        print(f"Got item from {url} Code: {response.status_code}")
        data = None
        if response.status_code == 200:
            data = json.loads(response.text)
        return data
   
def is_date_between(href, dates):
    href = href.split('/')[0]
    href_date = datetime.datetime.strptime(href, "%Y-%m-%d").date()
    return dates[0] <= href_date <= dates[1]

async def get_items(wrs_list, dates=None, limit=1):
    if not dates:
        delta = datetime.timedelta(days=30)
        today = datetime.datetime.now()
        dates = [(today - delta).date(), today.date()]
    
    base_url = "https://landsat-stac.s3.amazonaws.com/landsat-8-l1"
    links = [f"{base_url}/{wrs['path']:03d}/{wrs['row']:03d}/catalog.json" for wrs in wrs_list]
    tasks = [get_item(link) for link in links[:limit]]
    catalogs = await asyncio.gather(*tasks)
    catalogs = [catalog for catalog in catalogs if catalog]

    links = []
    for catalog in catalogs:
        base_url = [link['href'] for link in catalog['links'] if link['rel'] == 'self'][0]
        base_url = base_url.replace('catalog.json', '')
        links += [f"{base_url}{link['href']}" for link in catalog['links'] if link['rel'] == 'item' and is_date_between(link['href'], dates)]

    tasks = [get_item(link) for link in links[:limit]]
    result = await asyncio.gather(*tasks)
    return result
    

def get_geo_ref_points(points):

    lons = (points[0], points[2])
    lats = (points[1], points[3])

    minlon = min(lons)
    minlat = min(lats)
    maxlon = max(lons)
    maxlat = max(lats)

    return {
        'ul': {'x': minlon, 'y': maxlat},
        'ur': {'x': maxlon, 'y': maxlat},
        'll': {'x': minlon, 'y': minlat},
        'lr': {'x': maxlon, 'y': minlat},
    }

def item_to_metadata(item):
    bands = [('1', 'coastal_aerosol'),
             ('2', 'blue'),
             ('3', 'green'),
             ('4', 'red'),
             ('5', 'nir'),
             ('6', 'swir1'),
             ('7', 'swir2'),
             ('8', 'panchromatic'),
             ('9', 'cirrus'),
             ('10', 'lwir1'),
             ('11', 'lwir2'),
             ('QA', 'quality')]
    coordinates = item['bbox']
    cs_code = '4326'
    geo_ref_points = get_geo_ref_points(coordinates)
    doc = {
        'id': str(uuid.uuid5(uuid.NAMESPACE_URL, item['id'])),
        'processing_level': item['properties']['landsat:processing_level'],
        'product_type': item['properties']['landsat:processing_level'], #item['properties']['collection'], 
        'creation_dt': item['properties']['datetime'],
        'label': item['properties']['landsat:scene_id'],
        'platform': {'code': 'LANDSAT_8'},
        'instrument': {'name': 'OLI_TIRS'},
        'extent': {
            'from_dt': item['properties']['datetime'],
            'to_dt': item['properties']['datetime'],
            'center_dt': item['properties']['datetime'],
            'coord': geo_ref_points,
        },
        'format': {'name': 'GeoTiff'},
        'grid_spatial': {
            'projection': {
                'geo_ref_points': geo_ref_points,
                'spatial_reference': 'EPSG:%s' % cs_code,
            }
        },
        'image': {
            'bands': {
                band[1]: {
                    'path': item['assets'][f'B{band[0]}']['href'],
                    'layer': 1,
                } for band in bands
            }
        },
        'lineage': {'source_datasets': {}},
    }
    return doc

def add_dataset(doc):
    dc = datacube.Datacube(config='datacube.conf')
    print(dc)
    index = dc.index
    print(index)
    resolver = Doc2Dataset(index)
    print(resolver)
    dataset, error = resolver(doc, 'file:///tmp/test-dataset.json')
    print(dataset, error)
    index.datasets.add(dataset)


async def main(wrs_list):
    result = await get_items(wrs_list, limit=1)
    pprint.pprint(len(result))
    for item in result:
        doc = item_to_metadata(item)
        pprint.pprint(doc)
        add_dataset(doc)

if __name__ == "__main__":
    wrs = ConvertToWRS()
    lonlat = (130., 40., 135., 45.)
    wrs_list = wrs.get_wrs_list(*lonlat)
    asyncio.run(main(wrs_list))