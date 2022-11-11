import asyncio
import json
import time

import aiohttp
import datetime

from fake_useragent import UserAgent

result = []
lose_pages = []


async def get_page_data(session, page, tyre):
    try:
        type_result = []
        ua = UserAgent()
        headers = {
            'User-Agent': ua.random,
            'X-Requested-With': 'XMLHttpRequest'
        }
        url = f'https://roscarservis.ru/catalog/{tyre}/?set_filter=Y&sort%5Brecommendations%5D=asc&PAGEN_1={page}'
        async with session.get(url=url, headers=headers) as response:
            response_text = await response.json(content_type='text/html')
            items = response_text.get('items')
            for item in items:
                item_name = item['name']
                item_price = item['price']
                item_amount = item['amount']
                item_img = item['imgSrc']
                item_url = item['url']
                type_result.append({
                    'name': item_name,
                    'type': tyre,
                    'price': item_price,
                    'amount': item_amount,
                    'img': item_img,
                    'url': item_url,
                })
            result.append(type_result)
            print(f'Обработана страница {page} - {tyre}')

    except json.decoder.JSONDecodeError:
        lose_pages.append({tyre: page})


async def gather_data(tyre):
    ua = UserAgent()
    headers = {
        'User-Agent': ua.random,
        'X-Requested-With': 'XMLHttpRequest'
    }
    url = f'https://roscarservis.ru/catalog/{tyre}'
    async with aiohttp.ClientSession() as session:
        response = await session.get(url=url, headers=headers)
        pages_count = (await response.json(content_type='text/html')).get('pagesCount')
        tasks = []
        for page in range(1, pages_count + 1):
            task = asyncio.create_task(get_page_data(session, page, tyre))
            tasks.append(task)
        await asyncio.gather(*tasks)


def main():
    start_time = time.time()
    tires = ['legkovye', 'diskont', 'legkogruzovye', 'gruzovye', 'selskohozyaystvenye', 'specshiny']
    for tyre in tires:
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(gather_data(tyre))
    current_time = datetime.datetime.now().strftime('%m-%d-%Y')
    with open(f'data/{current_time}roscar_async.json', 'w', encoding='utf-8') as file:
        json.dump(result, file, indent=4, ensure_ascii=False)
    diff_time = time.time() - start_time
    print(f'Затраченное время на работу скрипта - {diff_time}')
    print(lose_pages)


if __name__ == '__main__':
    main()
