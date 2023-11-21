import PyPDF2
import re
from datetime import datetime
import glob
import os


def create_new_name(old_file_name: str) -> list:
    with open(old_file_name, 'rb') as pdfFileObj:
        pdfReader = PyPDF2.PdfReader(pdfFileObj)
        pageObj = pdfReader.pages[0]
        text = pageObj.extract_text()
    pattern1 = r'[a-zA-Zа-яА-ЯёЁ]{2}\d{6}\u00ad\d{2}'
    number = re.findall(pattern1, text)[0].replace('\u00ad', '-')
    pattern2 = r'\d{2}\.\d{2}\.\d{4}'
    dates = re.findall(pattern2, text)
    max_data = '.'.join(list(reversed(str(max([datetime.strptime(i, '%d.%m.%Y') for i in dates]))[:10].split('-'))))
    try:
        name_driver = find_name_driver(old_file_name)
    except:
        name_driver = 'NO NAME'
    print(name_driver)
    new_file_name = f'{number} {max_data}'
    if len(new_file_name) == 22:
        new_file_name += f' {name_driver}.pdf'
        return [old_file_name, new_file_name]
    return None


def find_pdf_files() -> list:
    return glob.glob('AxaptaReport*.pdf')


def find_name_driver(old_file_name: str) -> str:
    with open(old_file_name, 'rb') as pdfFileObj:
        pdfReader = PyPDF2.PdfReader(pdfFileObj)
        max_page = list(pdfReader.pages)
        pageObj = pdfReader.pages[len(max_page) - 1]
        text = pageObj.extract_text()
    pattern = r'(?<=Выданной : )[а-яА-ЯёЁ]*'
    return re.search(pattern, text)[0]
    


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


if __name__ == '__main__':
    pdf_files = find_pdf_files()
    old_new_files = [create_new_name(i) for i in pdf_files]
    print(f'{old_new_files = }')
    error = check_unique(old_new_files)
    print(f'{error = }')
    not_rename = [item for sublist in error.values() for item in sublist]
    print(f'{not_rename = }')
    for old, new in old_new_files:
        if not old in not_rename:
            rename_file(old, new)
    if error:
        create_error_report(error)


