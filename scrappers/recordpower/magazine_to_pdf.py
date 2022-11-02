import os
import requests
import img2pdf


def get_data():
    headers = {

        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/107.0.0.0 Safari/537.36 '
    }

    for i in range(1, 49):
        url = f'https://www.recordpower.co.uk/flip/Winter2020/files/mobile/{i}.jpg'
        req = requests.get(url=url, headers=headers)
        response = req.content
        with open(f'data/media/picture{i}.jpg', 'wb') as file:
            file.write(response)
            print(f'{i} of 48 downloaded')


def convert_img_to_pdf():
    img_list = [f'data/media/picture{i}.jpg' for i in range(1, 49)]
    with open('data/result.pdf', 'wb') as file:
        file.write(img2pdf.convert(img_list))


def main():
    if not os.listdir('data/media'):
        get_data()
    convert_img_to_pdf()


if __name__ == '__main__':
    main()
