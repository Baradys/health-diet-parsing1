import json
import time
import os

import asyncio
import aiohttp

from aiohttp_socks import ProxyConnector
from fake_useragent import UserAgent

from dotenv import load_dotenv

load_dotenv()

TEST_LOGIN = str(os.environ.get('LOGIN'))
TEST_PASSWORD = str(os.environ.get('PASSWORD'))

all_categories = {}


def get_headers():
    ua = UserAgent()
    fake_ua = {'user-agent': ua.random}
    return fake_ua


async def get_data(session, url, headers):
    nutrients_dict = {'11': 'Калории', '13': 'Белки', '14': 'Жиры', '15': 'Углеводы', '12': 'Вода', '18': 'Клетчатка'}
    async with session.get(url, headers=headers) as response:
        if response.status == 200 and (await response.json()).get('name_group') != 'удалённые':
            nutrients_json = {}
            item_data = {}
            item = (await response.json())
            for nutrients_id, nutrients_name in nutrients_dict.items():
                if isinstance(item.get('nutrients'), dict):
                    nutrients_json[nutrients_name] = item.get('nutrients').get(nutrients_id, 0)
            item_data[item.get('name')] = nutrients_json
            try:
                all_categories[item.get('name_group')].append(item_data)
            except KeyError:
                all_categories[item.get('name_group')] = []
                all_categories[item.get('name_group')].append(item_data)


async def main():
    start = time.time()
    connector = ProxyConnector.from_url(f'socks5://{TEST_LOGIN}:{TEST_PASSWORD}@194.242.126.219:8000')
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = []
        for counter in range(0, 25000):
            url = f'https://health-diet.ru/api2/base_of_food/common/{counter}.json?10'
            if counter % 100 == 0:
                print(counter)
            headers = get_headers()
            task = asyncio.create_task(get_data(session, url, headers))
            tasks.append(task)
            await asyncio.gather(*tasks)

    with open('data/health_diet_data.json', 'w') as file:
        json.dump(all_categories, file, indent=4, ensure_ascii=False)
    finish = time.time()
    print(finish - start)


if __name__ == '__main__':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
