import re

import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime


def get_data():
    current_data = datetime.now().strftime('%d-%m-%Y')
    url = 'https://www.muztorg.ru/category/akusticheskie-gitary'
    response = requests.get(url=url).text
    soup = BeautifulSoup(response, 'lxml')
    guitars = soup.find_all('div', class_='product-caption')
    data = []
    for guitar in guitars:
        name = str(guitar.findNext(class_='title').findNext('meta')['content']).split(' ', 1)
        brand = name[0]
        model = name[1]
        price = guitar.findNext('meta', {'itemprop': 'price'})['content']
        link = 'https://www.muztorg.ru' + guitar.findNext('div', class_='product-catalog-grid').findNext('a')['href']
        data.append(
            {
                'product_brand': brand,
                'product_model': model,
                'product_link': link,
                'product_price': price,
            }
        )
    with open(f'guitars/data_{current_data}.json', 'w') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


def main():
    get_data()


if __name__ == '__main__':
    main()
