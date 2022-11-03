import re

from fake_useragent import UserAgent
from bs4 import BeautifulSoup
import requests


def get_data():
    ua = UserAgent()
    fake_ua = {'user-agent': ua.random}
    url = 'https://tury.ru/hotel/'
    req = requests.get(url=url, headers=fake_ua)
    response = req.text
    soup = BeautifulSoup(response, 'lxml')
    location_li = soup.find(class_='select__selected-list scroll').find_all('li')
    location_dict = {}
    for country in location_li:
        location = re.search(r'(?<=span>).+(?=</span)', str(country)).group().strip()
        index = int(re.search(r'(?<=\.val\(\')\d+(?=\')', str(country)).group())
        location_dict[location] = index
    new_string_char = '\n'
    your_location_index = location_dict[
        input(
            f'Choose your location from list: '
            f'{new_string_char + new_string_char.join(location_dict.keys()) + new_string_char}'
            f'Enter state: ')]
    for i in range(0, 40, 20):
        location_url = f'https://tury.ru/hotel/?cn={your_location_index}&s={i}'
        response = requests.get(url=location_url).text
        soup = BeautifulSoup(response, 'lxml')
        hotels = [hotel['href'] for hotel in soup.find_all('a', class_='reviews-travel__title')]
        if not hotels:
            break
        for link in hotels:
            link_re = re.search(r"(?<=\d-).+", link)
            if not link_re:
                continue
            print(link)
            req = requests.get(url=link, headers=fake_ua)
            with open(f'data/{link_re.group()}.html', 'w', encoding='utf-8') as file:
                file.write(req.text)


def main():
    get_data()


if __name__ == '__main__':
    main()
