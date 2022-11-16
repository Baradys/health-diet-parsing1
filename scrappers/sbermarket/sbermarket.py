import json
import os


from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By


items_result = []


def get_data(search):
    url = f'https://sbermegamarket.ru/catalog/?q={search}#?filters=%7B"4CB2C27EAAFC4EB39378C4B7487E6C9E"%3A%5B"1"%5D%7D'
    with webdriver.Chrome() as browser:
        browser.get(url=url)
        try:
            last_page = int(browser.find_element(By.CLASS_NAME, 'full').find_elements(By.TAG_NAME, 'a')[-2].text.strip())
        except NoSuchElementException:
            last_page = 1
        for page in range(1, last_page + 1)[:2]:
            url = f'https://sbermegamarket.ru/catalog/page-{page}/?q={search}#?filters=%7B"4CB2C27EAAFC4EB39378C4B7487E6C9E"%3A%5B"1"%5D%7D'
            browser.get(url=url)
            items = browser.find_elements(By.CLASS_NAME, 'catalog-item')
            for item in items:
                item_price = int(item.find_element(By.CLASS_NAME, 'item-price').text.replace(' ', '').replace('₽', ''))
                item_name = item.find_element(By.CLASS_NAME, 'item-title').text
                item_url = item.find_element(By.CLASS_NAME, 'item-title').find_element(By.TAG_NAME, 'a').get_attribute('href').split('#')[0]
                try:
                    old_price = int(
                        item.find_element(By.CLASS_NAME, 'item-old-price__price').text.replace(' ', '').replace('₽', ''))
                    if old_price > item_price:
                        discount = round((old_price - item_price) / old_price * 100)
                    else:
                        discount = 0
                except NoSuchElementException:
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
    if not os.path.exists('data'):
        os.mkdir('data')
    with open('data/sbermarket.json', 'w', encoding='utf-8') as file:
        json.dump(items_result, file, indent=4, ensure_ascii=False)


def main():
    search_data = '%20'.join(input('Поиск: ').split())
    get_data(search_data)


if __name__ == '__main__':
    main()
