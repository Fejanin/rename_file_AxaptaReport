import PyPDF2
import re
from datetime import datetime
import glob
import os


def create_new_name(old_file_name: str) -> list:
    text_first_page = read_text(old_file_name)
    text_last_page = read_text(old_file_name, first=False)
    try:
        number = find_invoice_name(text_first_page)
    except:
        number = 'NO000000-00'
    try:
        max_data = find_data(text_first_page)
    except:
        max_data = '00.00.0000'
    try:
        name_driver = find_name_driver(text_last_page)
    except:
        name_driver = 'NO NAME'
    try:
        name_company = find_name_company(text_first_page)
    except:
        name_company = 'NO COMPANY'
    try:
        weight = find_weight(text_last_page)
    except:
        weight = '0.0'
    new_file_name = f'{name_company} {number} {max_data} {name_driver} {weight}кг.pdf'
    return [old_file_name, new_file_name]


def find_weight(text):
    pattern = r'(?<=Отпуск груза произвел)[0-9\s]*'
    return ''.join(re.search(pattern, text)[0].split())


def find_invoice_name(text):
    pattern = r'[a-zA-Zа-яА-ЯёЁ]{2}\d{6}\u00ad\d{2}'
    return re.findall(pattern, text)[0].replace('\u00ad', '-')


def find_data(text):
    pattern = r'\d{2}\.\d{2}\.\d{4}'
    dates = re.findall(pattern, text)
    return '.'.join(list(reversed(str(max([datetime.strptime(i, '%d.%m.%Y') for i in dates]))[:10].split('-'))))


def find_pdf_files() -> list:
    return glob.glob('AxaptaReport*.[pP][dD][fF]')


def find_name_driver(text: str) -> str:
    pattern = r'(?<=Выданной : )[а-яА-ЯёЁ]*'
    return re.search(pattern, text)[0]


def find_name_company(text: str) -> str:
    pattern = r'ООО\s\"[А-Яа-яЁё\s]+\"'
    res = re.search(pattern, text)[0].replace('\xa0', ' ').replace('"', '')
    return res


def check_unique(data: list) -> list:
    all_files = {}
    error = {}
    for i in data:
        if not i[1] in all_files:
            all_files[i[1]] = i[0]
        else:
            td = error.get(i[1], [all_files[i[1]]])
            td.append(i[0])
            error[i[1]] = td
    return error


def rename_file(old_name: str, new_name: str) -> None:
    os.rename(old_name, new_name)


def create_error_report(error: dict) -> None:
    with open('ERROR.txt', 'w') as f:
        for key, value in error.items():
            f.write(f'{key}: {value}')

def read_text(old_file_name: str, first=True) -> str:
    with open(old_file_name, 'rb') as pdfFileObj:
        pdfReader = PyPDF2.PdfReader(pdfFileObj)
        if first:
            pageObj = pdfReader.pages[0]
        else:
            max_page = list(pdfReader.pages)
            pageObj = pdfReader.pages[len(max_page) - 1]
        return pageObj.extract_text()



if __name__ == '__main__':
    pdf_files = find_pdf_files()
    old_new_files = [create_new_name(i) for i in pdf_files]
    #print(f'{old_new_files = }')
    error = check_unique(old_new_files)
    #print(f'{error = }')
    not_rename = [item for sublist in error.values() for item in sublist]
    #print(f'{not_rename = }')
    for old, new in old_new_files:
        if not old in not_rename:
            rename_file(old, new)
    if error:
        create_error_report(error)


