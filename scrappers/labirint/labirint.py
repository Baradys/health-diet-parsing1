import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent


def get_data():
    ua = UserAgent()
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,'
                  'application/signed-exchange;v=b3;q=0.9',
        'User-Agent': ua.random,
    }
    url = 'https://www.labirint.ru/genres/2498/?display=table&available=1'
    response = requests.get(url=url, headers=headers)
    soup = BeautifulSoup(response.text, 'lxml')
    pages_count = int(soup.find('div', class_='pagination-numbers').find_all('a')[-1].text.strip())
    for page in range(2, 3):
        url = f'https://www.labirint.ru/genres/2498/?display=table&available=1&page={page}'
        response = requests.get(url=url, headers=headers)
        soup = BeautifulSoup(response.text, 'lxml')
        books = soup.find('tbody', class_='products-table__body').find_all('tr')
        for book in books:
            book_data = book.find_all('td')
            try:
                book_title = book_data[0].find('a').text
                if not book_title:
                    continue
            except AttributeError:
                continue
            try:
                book_author = ', '.join(list(map(lambda link: link.text, book_data[1].find_all('a'))))
            except AttributeError:
                book_author = 'Нет автора'
            try:
                book_publisher = ': '.join(list(map(lambda publisher: publisher.text, book_data[2].find_all('a'))))
            except AttributeError:
                book_publisher = 'Нет издательства'
            try:
                old_price = int(book_data[3].find(class_='price-gray').text.replace('₽', '').replace(' ', '').strip())
            except AttributeError:
                old_price = 'Нет старой цены'
            try:
                new_price = int(book_data[3].find(class_='price-val').text.replace('₽', '').replace(' ', '').strip())
            except AttributeError:
                new_price = 'Нет новой цены'
            try:
                discount = f'{round(((old_price - new_price) / old_price) * 100, 2)} %'
            except TypeError:
                discount = 'Скидки нет'


def main():
    get_data()


if __name__ == '__main__':
    main()
