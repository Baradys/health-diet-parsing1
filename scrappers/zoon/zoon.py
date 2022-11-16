import json
import re
import time
import os
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from fake_useragent import UserAgent
from urllib.parse import unquote

ua = UserAgent()
headers = {
    'User-Agent': ua.random,
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,'
              'application/signed-exchange;v=b3;q=0.9'
}

data_result = []


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


def get_data(urls):
    with open(urls, encoding='utf-8') as file:
        urls_list = [i.strip() for i in file.readlines()]
    counter = 1
    for url in urls_list:
        response = requests.get(url=url, headers=headers)
        soup = BeautifulSoup(response.text, 'lxml')
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
        print(f'{counter}/{len(urls_list)} handled')
        counter += 1


def main():
    get_source('https://spb.zoon.ru/medical/')
    get_urls('data/source_page.html')
    get_data('data/item_urls.txt')
    with open('data/zoon.json', 'w', encoding='utf-8') as file:
        json.dump(data_result, file, indent=4, ensure_ascii=False)


if __name__ == '__main__':
    main()
