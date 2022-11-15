import asyncio
import json
import re
import time
import os

import aiohttp
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from fake_useragent import UserAgent
from urllib.parse import unquote

from aiohttp_socks import ProxyConnector, ChainProxyConnector

load_dotenv()

TEST_LOGIN = str(os.environ.get('LOGIN'))
TEST_PASSWORD = str(os.environ.get('PASSWORD'))

ua = UserAgent()
headers = {
    'User-Agent': ua.random,
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,'
              'application/signed-exchange;v=b3;q=0.9'
}

data_result = []
counter = 0


def get_source(url):
    with webdriver.Chrome() as browser:
        browser.maximize_window()
        browser.get(url=url)
        while True:
            end_of_page = browser.find_element(By.CLASS_NAME, 'list-rating-info')
            more_button = browser.find_element(By.CLASS_NAME, 'catalog-button-showMore')
            if more_button.get_attribute('style') == 'display: none;':
                if not os.path.exists('data'):
                    os.mkdir('data')
                with open('data/source_page.html', 'w', encoding='utf-8') as file:
                    file.write(browser.page_source)
                break
            else:
                actions = ActionChains(browser)
                actions.move_to_element(end_of_page).perform()
                time.sleep(1)


def get_urls(data):
    with open(data, encoding='utf-8') as file:
        src = file.read()
    soup = BeautifulSoup(src, 'lxml')
    cards = soup.find('ul', class_='service-items-medium').find_all('li', class_='minicard-item')
    with open('data/item_urls.txt', 'w', encoding='utf-8') as file:
        file.write('\n'.join([i.find_next('a', class_='title-link')['href'] for i in cards]))


async def get_data(session, url, urls_list, retry=5):
    try:
        async with session.get(url=url, headers=headers) as response:
            response_text = await response.text()
            soup = BeautifulSoup(response_text, 'lxml')
            if response.status == 200:
                try:
                    item_name = soup.find('span', {'itemprop': 'name'}).text.replace(' ', ' ')
                except AttributeError:
                    item_name = None
                try:
                    phone_list = soup.find('div', class_='service-phones-list').find_all('a', class_='tel-phone')
                    item_phone = [i['href'].split(":")[1] for i in phone_list]
                except AttributeError:
                    item_phone = None
                try:
                    item_address = soup.find('address', {'itemprop': 'address'}).text.replace(' ', ' ')
                except AttributeError:
                    item_address = None
                try:
                    item_site = soup.find(text=re.compile('Компания в сети')).find_next().find_all('a')[0].text.strip()
                except AttributeError:
                    item_site = None
                try:
                    social_network_list = soup.find('div', class_='js-service-socials').findAll('a')
                    social_networks = [re.search(r'(?<=\?to=)[\w:/.-]+(?=&)', unquote(i['href'])).group() for i in
                                       social_network_list]
                except AttributeError:
                    social_networks = None
                data_result.append(
                    {
                        'item_name': item_name,
                        'item_phone': item_phone,
                        'url': url,
                        'item_address': item_address,
                        'item_site': item_site,
                        'social_networks': social_networks,
                    }
                )
                global counter
                counter += 1
                print(f'{counter}/{urls_list}')
            else:
                print(soup.text)  # Нужно проверить 512 статус код, каптча не пускает на сайт.
                try:
                    soup.find('button', class_='captcha-button').click()
                except Exception as ex:
                    print(ex)
                finally:
                    await asyncio.sleep(5)
    except Exception as ex:
        if retry:
            print(f'[INFO] {ex}: retry={retry} => {url}')
            await asyncio.sleep(60)
            return await get_data(session, url, urls_list, retry=(retry - 1))


async def gather_data(urls):
    connector = ProxyConnector.from_url(f'socks5://{TEST_LOGIN}:{TEST_PASSWORD}@45.95.149.229:8000')
    with open(urls, encoding='utf-8') as file:
        urls_list = [i.strip() for i in file.readlines()]
    async with aiohttp.ClientSession(connector=connector, trust_env=True) as session:
        tasks = []
        for url in urls_list:
            task = asyncio.create_task(get_data(session, url, len(urls_list)))
            tasks.append(task)
        await asyncio.gather(*tasks)


def main():
    get_source('https://spb.zoon.ru/medical/')
    get_urls('data/source_page.html')
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(gather_data('data/item_urls.txt'))
    with open('data/zoon.json', 'w', encoding='utf-8') as file:
        json.dump(data_result, file, indent=4, ensure_ascii=False)


if __name__ == '__main__':
    main()
