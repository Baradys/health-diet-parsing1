import json
import os

import requests
import datetime

from dotenv import load_dotenv
from fake_useragent import UserAgent

load_dotenv()

TEST_LOGIN = str(os.environ.get('LOGIN'))
TEST_PASSWORD = str(os.environ.get('PASSWORD'))

ua = UserAgent()
headers = {
    'User-Agent': ua.random,
    'X-Requested-With': 'XMLHttpRequest'
}


def get_data():
    data_result = []
    proxy = {'https': f'socks5://{TEST_LOGIN}:{TEST_PASSWORD}@194.242.126.219:8000'}
    tires = ['legkovye', 'diskont', 'legkogruzovye', 'gruzovye', 'selskohozyaystvenye', 'specshiny']
    for tire_type in tires:
        print(f'--------------\n{tire_type} in progress\n--------------')
        type_result = []
        url = f'https://roscarservis.ru/catalog/{tire_type}'
        response = requests.get(url=url, headers=headers, proxies=proxy)
        pages_count = response.json()['pagesCount']
        for page in range(1, pages_count + 1):
            url = f'https://roscarservis.ru/catalog/{tire_type}/?set_filter=Y&sort%5Brecommendations%5D=asc&PAGEN_1={page}'
            response = requests.get(url=url, headers=headers, proxies=proxy)
            data = response.json()
            items = data['items']
            for item in items:
                item_name = item['name']
                item_price = item['price']
                item_amount = item['amount']
                item_img = item['imgSrc']
                item_url = item['url']
                type_result.append({
                    'name': item_name,
                    'price': item_price,
                    'amount': item_amount,
                    'img': item_img,
                    'url': item_url,
                })
            print(f'{page} of {pages_count} pages have been handled')
        data_result.append({
            f'{start_time.strftime("%d-%m-%Y")}-{tire_type}': type_result
        })
    return data_result


def main():
    global start_time
    start_time = datetime.datetime.now()
    with open('data/result.json', 'w', encoding='utf-8') as file:
        json.dump(get_data(), file, indent=4, ensure_ascii=False)
    print(datetime.datetime.now() - start_time)


if __name__ == '__main__':
    main()
