import json
import time

import requests
import os
from fake_useragent import UserAgent

ua = UserAgent()
headers = {
    'User-Agent': ua.random
}

result = []


def get_data_file():
    page = 1
    while True:
        print(page)
        url = f'https://www.landingfolio.com/api/inspiration?page={page}'
        response = requests.get(url=url, headers=headers)
        data = response.json()
        if not data:
            if os.path.exists('data'):
                pass
            else:
                os.mkdir('data')
            with open('data/landingfolio.json', 'w') as file:
                json.dump(result, file, indent=4, ensure_ascii=False)
            break
        for item in data:
            title = item['title']
            url = item['url']
            images_list = []
            for img in item['screenshots']:
                images = {
                    'desktop': f"https://landingfoliocom.imgix.net/{img['images']['desktop']}",
                    'mobile': f"https://landingfoliocom.imgix.net/{img['images']['mobile']}",
                    'type': img['title']
                }
                images_list.append(images)
            result.append({
                'title': title,
                'url': url,
                'images': images_list,
            })
        page += 1


def download_images(file_path):
    with open(file_path) as file:
        src = json.load(file)
    items_len = len(src)
    count = 1
    for item in src:
        item_name = item['title'].lower()
        item_images = item['images']
        if not os.path.exists(f'data/{item_name}'):
            os.mkdir(f'data/{item_name}')
        for img in item_images:
            request = requests.get(url=img['desktop'])
            with open(f'data/{item_name}/{img["type"]}-desktop.png', 'wb') as file:
                file.write(request.content)
            request = requests.get(url=img['mobile'])
            with open(f'data/{item_name}/{img["type"]}-mobile.png', 'wb') as file:
                file.write(request.content)
        print(f'{count}/{items_len} images downloaded')
        count += 1


def main():
    start = time.time()
    get_data_file()
    download_images('data/landingfolio.json')
    diff_time = time.time() - start
    print(diff_time)


if __name__ == '__main__':
    main()
