import json
import time

from aiohttp_socks import ProxyConnector
from fake_useragent import UserAgent
import asyncio
import aiohttp


def get_headers():
    ua = UserAgent()
    fake_ua = {'user-agent': ua.random}
    return fake_ua


async def get_data():
    connector = ProxyConnector.from_url('socks5://m2juGL:ua091T@194.242.126.219:8000')
    headers = get_headers()
    all_categories = {}
    nutrients_dict = {'11': 'Калории', '13': 'Белки', '14': 'Жиры', '15': 'Углеводы', '12': 'Вода', '18': 'Клетчатка'}
    for counter in range(24500, 24505):
        url = f'https://health-diet.ru/api2/base_of_food/common/{counter}.json?10'
        if counter % 100 == 0:
            print(counter)
            headers = get_headers()
        async with aiohttp.ClientSession() as session:
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
                    except Exception:
                        all_categories[item.get('name_group')] = []
                        all_categories[item.get('name_group')].append(item_data)
    return all_categories


async def main():
    start = time.time()
    with open('data/health_diet_data.json', 'w') as file:
        json.dump(await get_data(), file, indent=4, ensure_ascii=False)
    finish = time.time()
    print(finish - start)


if __name__ == '__main__':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
