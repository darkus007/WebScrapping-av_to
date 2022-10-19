import csv
import xlsxwriter
import json


def save_in_csv_file(data, file_name):
    with open(file_name + '.csv', 'w', newline='') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(['ID', 'Наименование', 'Цена', 'Место', 'Время публикации', 'Ссылка'])
        for item in data:
            writer.writerow([item['id'], item['item'], item['price'], item['place'], item['data_maker'], item['link']])
        print(f'Данные записаны в файл {file_name}.csv')


def save_in_xlsx_file(data, file_name):
    head = ('ID', 'Наименование', 'Цена', 'Место', 'Время публикации', 'Ссылка')
    # Create an new Excel file and add a worksheet.
    workbook = xlsxwriter.Workbook(file_name + '.xlsx')
    worksheet = workbook.add_worksheet()
    bold = workbook.add_format({'bold': True})      # Add a bold format to use to highlight cells.
    # write headers
    worksheet.write_row(0, 0, head, bold)
    # write data
    row = 1
    for item in data:
        worksheet.write_row(row, 0, [item['id'], item['item'], item['price'], item['place'], item['data_maker'],
                                     item['link']])
        row += 1
    workbook.close()
    print(f'Данные записаны в файл {file_name + ".xlsx"}')


def save_in_json_file(data, file_name):
    with open(f'{file_name}.json', 'w') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)
        print(f'Данные записаны в файл {file_name}.json')
