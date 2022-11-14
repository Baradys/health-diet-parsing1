import asyncio
import json
import time

import aiofiles
import aiohttp
import os
from fake_useragent import UserAgent

ua = UserAgent()
headers = {
    'User-Agent': ua.random
}

pages = []
result = []
counter = 0


async def get_pages(session):
    page = 1
    while True:
        url = f'https://www.landingfolio.com/api/inspiration?page={page}'
        async with session.get(url=url, headers=headers) as response:
            data = await response.json()
        if not data:
            return
        pages.append(page)
        page += 1


async def get_data_file(session, page):
    url = f'https://www.landingfolio.com/api/inspiration?page={page}'
    async with session.get(url=url, headers=headers) as response:
        data = await response.json()
        for item in data:
            title = item['title']
            url = item['url']
            images_list = []
            for img in item['screenshots']:
                images = {
                    'desktop': f"https://landingfoliocom.imgix.net/{img['images']['desktop']}",
                    'mobile': f"https://landingfoliocom.imgix.net/{img['images']['mobile']}",
                    'type': img['title']
                }
                images_list.append(images)
            result.append({
                'title': title,
                'url': url,
                'images': images_list,
            })


async def gather_pages():
    async with aiohttp.ClientSession() as session:
        tasks = []
        task = asyncio.create_task(get_pages(session))
        tasks.append(task)
        await asyncio.gather(*tasks)


async def gather_data():
    async with aiohttp.ClientSession() as session:
        tasks = []
        for page in pages:
            task = asyncio.create_task(get_data_file(session, page))
            tasks.append(task)
        await asyncio.gather(*tasks)


async def write_file(session, item_name, url, retry=5):
    global counter
    async with aiofiles.open(item_name, 'wb') as file:
        try:
            async with session.get(url) as response:
                async for part in response.content.iter_chunked(1024):
                    await asyncio.sleep(0)
                    await file.write(part)
        except asyncio.exceptions.TimeoutError:
            if retry:
                print(f'[INFO] TimeoutError retry={retry} => {url}')
                await asyncio.sleep(60)
                return await write_file(session, item_name, url, retry=(retry - 1))
        except aiohttp.ClientPayloadError:
            if retry:
                print(f'[INFO] PayloadError retry={retry} => {url}')
                await asyncio.sleep(60)
                return await write_file(session, item_name, url, retry=(retry - 1))



async def gather_images():
    async with aiohttp.ClientSession() as session:
        with open('data/landingfolio.json') as file:
            src = json.load(file)
        tasks = []
        for item in src:
            item_name = item['title'].lower()
            item_images = item['images']
            if not os.path.exists(f'data/{item_name}'):
                os.mkdir(f'data/{item_name}')
            for img in item_images:
                name_desktop = f'data/{item_name}/{img["type"]}-desktop.png'
                name_mobile = f'data/{item_name}/{img["type"]}-mobile.png'
                url_desktop = img['desktop']
                url_mobile = img['mobile']
                task_desktop = asyncio.create_task(write_file(session, name_desktop, url_desktop))
                task_mobile = asyncio.create_task(write_file(session, name_mobile, url_mobile))
                tasks.append(task_desktop)
                tasks.append(task_mobile)
        await asyncio.gather(*tasks)


def main():
    start = time.time()
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(gather_pages())
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(gather_data())
    if not os.path.exists('data'):
        os.mkdir('data')
    with open('data/landingfolio.json', 'w') as file:
        json.dump(result, file, indent=4, ensure_ascii=False)
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(gather_images())
    diff_time = time.time() - start
    print(diff_time)


if __name__ == '__main__':
    main()
