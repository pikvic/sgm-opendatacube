import json
import httpx
import pprint
import asyncio
import datetime
from helpers import ConvertToWRS


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
    
async def main(wrs_list):
    result = await get_items(wrs_list, limit=1000)

    pprint.pprint(len(result))

if __name__ == "__main__":
    wrs = ConvertToWRS()
    lonlat = (130., 40., 135., 45.)
    wrs_list = wrs.get_wrs_list(*lonlat)
    asyncio.run(main(wrs_list))