import datetime
import json

import requests
import datetime

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 '
                  'Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest'
}


def get_data():
    data_result = []
    tires = ['legkovye', 'diskont', 'legkogruzovye', 'gruzovye', 'selskohozyaystvenye', 'specshiny']
    for tire_type in tires:
        print(f'--------------\n{tire_type} in progress\n--------------')
        type_result = []
        url = f'https://roscarservis.ru/catalog/{tire_type}'
        response = requests.get(url=url, headers=headers)
        pages_count = response.json()['pagesCount']
        for page in range(1, pages_count + 1):
            url = f'https://roscarservis.ru/catalog/{tire_type}/?set_filter=Y&sort%5Brecommendations%5D=asc&PAGEN_1={page}'
            response = requests.get(url=url, headers=headers)

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
    # Готов данные для добавления в json файл. Осталось указать дату к tire_type и создавать файл


def main():
    global start_time
    start_time = datetime.datetime.now()
    with open('data/result.json', 'w', encoding='utf-8') as file:
        json.dump(get_data(), file, indent=4, ensure_ascii=False)
    print(datetime.datetime.now() - start_time)


if __name__ == '__main__':
    main()
