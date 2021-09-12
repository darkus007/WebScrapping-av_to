import os
import re
import datetime
import requests
from bs4 import BeautifulSoup as bs
from time import sleep
from random import randint
from save_in_file import *

HOST = "https://www.avito.ru"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/92.0.4515.107 Safari/537.36',
    'Accept': '*/*'}


def get_html(url, params=None):
    """Return html page or empty string"""
    try:
        rq = requests.get(url, params=params, headers=HEADERS)
        return rq
    except Exception as ex:
        print(ex)
        return ''


def get_number_of_pages(html_text):
    """Return number of pages (int)"""
    soup = bs(html_text, 'lxml')
    try:
        pages = soup.find('div', class_='pagination-root-Ntd_O').find_all('span')
    except AttributeError:
        return 1
    return int(pages[-2].get_text())


def get_content(html_text):
    """Scrapping data from one html page, and return list of dicts"""

    soup = bs(html_text, 'lxml')
    content = []
    try:
        # items = soup.find_all('div', class_="iva-item-body-NPl6W")
        # items = soup.find_all('div', class_="iva-item-body-R_Q9c")
        # иногда меняется класс (см выше), потому через регулярные вырадения:
        items = soup.find_all('div', class_=re.compile(r"iva-item-root-[\w]{5}"))
        for item in items:
            try:
                item_id = int(item.get('data-item-id'))
            except AttributeError:
                item_id = ''
            try:
                name = item.find(attrs={"itemprop": "name"}).get_text(strip=True)
            except AttributeError:
                name = 'Нет данных'
            try:
                temp = item.find(attrs={"itemprop": "price"}).get('content')    # иногда вместо цифр "Бесплатно"
                try:
                    price = int(temp)
                except ValueError:
                    price = temp
            except AttributeError:
                price = 'Нет данных'
            try:
                place = item.find("div", class_="geo-georeferences-Yd_m5 text-text-LurtD text-size-s-BxGpL")\
                                    .find_next('span').find_next('span').get_text()
            except AttributeError:
                place = 'Нет данных'
            try:
                data_maker = item.find(attrs={"data-marker": "item-date"}).get_text(strip=True)
            except AttributeError:
                data_maker = 'Нет данных'
            try:
                link = HOST + item.find('a', href=True).get('href')
            except AttributeError:
                link = 'Нет данных'
            content.append({'id': item_id, 'item': name, 'price': price, 'place': place, 'data_maker': data_maker,
                            'link': link})
    except AttributeError:
        print('На странице нет объявлений.')

    print(f'Получено {len(content)} объявлений на странице.')
    return content


def parse(url):
    """Scrapping data from all html pages, and return list of dicts"""

    html_page = get_html(url=url)

    if html_page.status_code == 200:
        number_of_pages = get_number_of_pages(html_page.text)

        content = []

        for page in range(1, number_of_pages + 1):
        # for page in range(1, 2):
            print(f'Парсим страницу {page} из {number_of_pages} ...', end='\t')

            # 'https://www.avito.ru/...&user=1'
            # 'https://www.avito.ru/...&user=1&p=2'
            # различается ключем р=2, где 2 - номер страницы
            html_page = get_html(url, params={'p': page})

            # получение результатов со страницы и добавление в итоговые результаты с игнором дубликатов
            content_from_page = get_content(html_page.text)
            for page_content in content_from_page:
                flag = True
                for all_content in content:
                    if page_content['id'] == all_content['id']:
                        flag = False
                if flag:
                    content.append(page_content)

            sleep(randint(2, 4))  # небольшая задержка в 2 - 4 с, что бы не нагружать сервер запросами

        print(f'Всего получено {len(content)} уникальных объявлений.')
        return content
    else:
        print('Ошибка открытия страницы!')
        return []


def compare_str(str_one, str_two):
    """Compare two string from 0 to first difference and return it (str)"""
    str_one_temp = str_one.lower()
    str_two_temp = str_two.lower()
    str_len = len(str_one)
    if len(str_two) < str_len:
        str_len = len(str_two)

    k = 0
    while k < str_len:
        if str_one_temp[k] == str_two_temp[k]:
            k += 1
        else:
            break
    return str_one[0:k]


def main():
    print('Данная программа предназначена для парсинга https://www.avito.ru/')
    print('Перейдите на страницу площадки, выберите товар, примените фильтры,')
    print('далее скопируйте адрес и введите его ниже.')
    print('==================================================================')
    url = input('Введите адрес страницы для парсинга и нажмите Enter:\n')
    url = url.strip()  # на всякий случай обрезаем пробелы в начале и конце страницы

    # парсим сайт
    #content = parse(url)

    # сохраняем результаты
    str_one = str(content[0]['item'])
    str_two = str(content[1]['item'])
    str_name = compare_str(str_one, str_two)
    # str_name = re.sub(r'[a-zA-Z]', lambda cap: cap.group().upper(), str_name, 1)   # делаем зашлавной 1 букву

    if not os.path.exists('data'):
        os.makedirs('data')

    file_name = 'data/' + str_name + ' ' + datetime.datetime.now().strftime("%Y.%m.%d %H.%M.%S")

    save_in_json_file(content, file_name)
    save_in_csv_file(content, file_name)
    save_in_xlsx_file(content, file_name)


if __name__ == '__main__':
    main()
