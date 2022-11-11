import time

from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import datetime
import csv
import json
import asyncio
import aiohttp

books_data = []


async def get_page_data(session, page):
    ua = UserAgent()
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,'
                  'application/signed-exchange;v=b3;q=0.9',
        'User-Agent': ua.random,
    }
    url = f'https://www.labirint.ru/genres/2498/?display=table&available=1&page={page}'
    async with session.get(url=url, headers=headers) as response:
        response_text = await response.text()
        soup = BeautifulSoup(response_text, 'lxml')
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
            try:
                availability = book_data[-1].find(class_='mt3 rang-available').text.replace(' ', '').strip()
            except AttributeError:
                availability = 'Нет данных'

            books_data.append(
                {
                    'book_title': book_title,
                    'book_author': book_author,
                    'book_publisher': book_publisher,
                    'old_price': f'{old_price}₽' if type(old_price) is int else old_price,
                    'new_price': f'{new_price}₽' if type(new_price) is int else new_price,
                    'discount': discount,
                    'availability': availability,
                }
            )
        print(f'Обработана страница {page}')


async def gather_data():
    ua = UserAgent()
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,'
                  'application/signed-exchange;v=b3;q=0.9',
        'User-Agent': ua.random,
    }
    url = 'https://www.labirint.ru/genres/2498/?display=table&available=1'

    async with aiohttp.ClientSession() as session:
        response = await session.get(url=url, headers=headers)
        soup = BeautifulSoup(await response.text(), 'lxml')
        pages_count = int(soup.find('div', class_='pagination-numbers').find_all('a')[-1].text.strip())
        tasks = []

        for page in range(1, pages_count + 1):
            task = asyncio.create_task(get_page_data(session, page))
            tasks.append(task)

        await asyncio.gather(*tasks)


def main():
    start_time = time.time()
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(gather_data())
    current_time = datetime.datetime.now().strftime('%m-%d-%Y')
    with open(f'data/{current_time}-labirint_async.json', 'w', encoding='utf-8') as file:
        json.dump(books_data, file, indent=4, ensure_ascii=False)
    with open(f'data/{current_time}_labirint_async.csv', 'w', newline='', encoding='utf-8-sig') as file:
        writer = csv.writer(file, delimiter=';')

        writer.writerow(
            [
                'Название книги',
                'Автор',
                'Издательство',
                'Цена без скидки',
                'Цена со скидкой',
                'Процент скидки',
                'Наличие на складе'
            ]
        )
    for book in books_data:
        with open(f'data/{current_time}_labirint_async.csv', 'a', newline='', encoding='utf-8-sig') as file:
            writer = csv.writer(file, delimiter=';')

            writer.writerow(
                [
                    book['book_title'],
                    book['book_author'],
                    book['book_publisher'],
                    f'{book["old_price"]}₽' if type(book['old_price']) is int else book['old_price'],
                    f'{book["new_price"]}₽' if type(book['new_price']) is int else book['new_price'],
                    book['discount'],
                    book['availability']
                ]
            )

    diff_time = time.time() - start_time
    print(f'Затраченное время на работу скрипта - {diff_time}')


if __name__ == '__main__':
    main()
