import json
import os
import time

from bs4 import BeautifulSoup
from selenium import webdriver


def get_data(search, user_id=None):
    items_result = []
    url = f'https://sbermegamarket.ru/catalog/?q={search}#?filters=%7B"4CB2C27EAAFC4EB39378C4B7487E6C9E"%3A%5B"1"%5D%7D'
    with webdriver.Chrome() as browser:
        browser.get(url=url)
        time.sleep(5)
        response = browser.page_source
        soup = BeautifulSoup(response, 'lxml')
        try:
            last_page = int(soup.find('ul', class_='full').find_all('a')[-2].text.strip())
        except AttributeError:
            last_page = 1
        for page in range(1, last_page + 1)[:2]:
            url = f'https://sbermegamarket.ru/catalog/page-{page}/?q={search}#?filters=%7B"4CB2C27EAAFC4EB39378C4B7487E6C9E"%3A%5B"1"%5D%7D'
            browser.get(url=url)
            response = browser.page_source
            soup = BeautifulSoup(response, 'lxml')
            items = soup.find_all('div', class_='catalog-item')
            for item in items:
                item_price = int(item.find('div', class_='item-price').text.replace(' ', '').replace('₽', ''))
                item_name = item.find('div', class_='item-title').text.replace(' ', '')
                item_url = f"https://sbermegamarket.ru{item.find('div', class_='item-title').find('a')['href'].split('#')[0]}"
                try:
                    old_price = int(item.find('span', class_='item-old-price__price').text.replace(' ', '').replace('₽', ''))
                    if old_price > item_price:
                        discount = round((old_price - item_price) / old_price * 100)
                    else:
                        discount = 0
                except AttributeError:
                    old_price = None
                    discount = 0
                if discount:
                    items_result.append(
                        {
                            'item_name': item_name,
                            'item_price': item_price,
                            'old_price': old_price,
                            'discount': discount,
                            'url': item_url,
                        }
                    )
    items_result = sorted(items_result, key=(lambda x: x['discount']), reverse=True)
    if not os.path.exists('data'):
        os.mkdir('data')
    with open(f'data/sbermarket-{user_id}.json', 'w', encoding='utf-8') as file:
        json.dump(items_result, file, indent=4, ensure_ascii=False)


def main():
    search_data = '%20'.join(input('Поиск: ').split())
    get_data(search_data)


if __name__ == '__main__':
    main()
