import os
import re
import requests
import pymupdf

from urllib.parse import unquote
from bs4 import BeautifulSoup as bs
from functools import reduce

from nautica.api import Config

from src.lib.schedule.Parser import delete_spaces

def fetch_page(url: str) -> str:
    res = requests.get(url, timeout=10)
    res.raise_for_status()
    return res.text

def clean_filename(link: str, shorter_table: dict) -> str:
    match = re.findall(r'\d\d.\d\d.\d\d', link)
    date = match[-1] if match else ""

    name = reduce(lambda x, y: x.replace(y, shorter_table[y]), shorter_table, link.split('/')[-1].replace(date, ''))
    return delete_spaces(name).strip()

def download_pdf(url: str, save_path: str):
    resp = requests.get(url, allow_redirects=True, timeout=10)
    resp.raise_for_status()
    with open(save_path, 'wb') as f:
        f.write(resp.content)

def prepare_temp_dir(path: str):
    os.makedirs(path, exist_ok=True)
    for f in os.listdir(path):
        os.remove(os.path.join(path, f))

def download_timetables() -> list[dict]:
    temp_dir = Config("vki")["schedules.pdfTemp"]
    prepare_temp_dir(temp_dir)

    result = []

    html_text = fetch_page('https://ci.nsu.ru/education/schedule/')
    with open(f'{temp_dir}/page.html', 'w', encoding="utf-8") as f:
        f.write(html_text)

    soup = bs(html_text, 'html.parser')
    links = [unquote(a['href'].strip()) for a in soup.find_all('a', class_='file-link')]

    for link in links:
        if 'Основное' in link:
            continue

        tt_name = clean_filename(link, shorter_table)

        pdf_url = 'https://ci.nsu.ru' + link if not link.startswith('https://') else link
        pdf_path = f"{temp_dir}/{tt_name}.pdf"
        download_pdf(pdf_url, pdf_path)

        result.append({
            "path": pdf_path,
            "text": extract_text_from_pdf(pdf_path)
        })

    return result

def extract_text_from_pdf(pdf_path: str) -> str:
    doc = pymupdf.Document(pdf_path)
    return ''.join([page.get_text() for page in doc])

shorter_table = {
    '.pdf': '',
    '\n': '',
    'Расписание': '',
    'студентов': '',
    'преподователей': '',
    'курса': 'курс',
    'специальности ': '',
    'специальностей ': '',
    '09.02.07': 'прога',
    '09.02.01': 'железо',
    '09.02.08': '', 
    '01.02.08': '',
    'и': '',
    ' класса': 'клс.',
    'после ': '',
    'на': '',
    'Информационные системы и программирование': 'прога',
    'Компьютерные системы и комплексы': 'железо',
}