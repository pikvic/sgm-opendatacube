import json
import httpx
import pprint
import asyncio
from helpers import ConvertToWRS


async def get_item(url):
    async with httpx.AsyncClient() as client:
        print(f"Getting item from {url}")
        response = await client.get(url)
        print(f"Got item from {url}")
        data = json.loads(response.text)
        return data
   
async def get_items(path, row, limit=1):
    url = f"https://landsat-stac.s3.amazonaws.com/landsat-8-l1/{path:03d}/{row:03d}/catalog.json"
    with httpx.Client() as client:
        response = client.get('https://www.example.com/')
    response = httpx.get(url)
    data = json.loads(response.text)
    base_url = url.replace('catalog.json', '')
    links = [f"{base_url}{link['href']}" for link in data['links'] if link['rel'] == 'item']

    tasks = [get_item(link) for link in links[:limit]]
    result = await asyncio.gather(*tasks)
    return result
    
async def main():
    result = await get_items(17, 110)
    pprint.pprint(result)

if __name__ == "__main__":
    wrs = ConvertToWRS()
    lonlat = (130., 40., 135., 45.)
    result = wrs.get_wrs_list(*lonlat)
    print(result)
    #asyncio.run(main())