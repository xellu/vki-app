# async def get_all_timetables()-> list[Timetable]:
#     '''скачивает все pdf ки с сайта'''
#     if not os.path.exists(cfg.base_dir / 'temp/pdf_files'): os.makedirs(cfg.base_dir / 'temp/pdf_files')
#     for i in os.listdir(cfg.base_dir/'temp/pdf_files/'): os.remove(cfg.base_dir/'temp/pdf_files'/i)
#     result = []
#     async with aiohttp.ClientSession(trust_env=True) as sesion:
#         async with sesion.get('https://ci.nsu.ru/education/schedule/', timeout=aiohttp.ClientTimeout(10)) as resp:
#             with open(cfg.base_dir/'temp/pagecopy.html', 'w') as file:
#                 file.write(await resp.text())
#             soup = BS(await resp.text(), 'html.parser')
#             items = soup.find_all('a', class_='file-link')
#             for i in items:
#                 link = unquote(i.get('href').replace('\n','').strip())
#                 if 'Основное' in link: continue
#                 date = re.findall(r'\d\d.\d\d.\d\d', link)[-1] or ''
#                 tt = Timetable(
#                     name=delete_spaces(reduce(lambda x,y: x.replace(y, shorter_table[y]), shorter_table, link.split('/')[-1].replace(date,''))).strip(),
#                     # name=link.split('/')[-1].translate(shorter_table).replace(date,'').strip(),
#                     # name=link.split('/')[-1].replace('.pdf','').replace('\n','').replace('Расписание','').replace('студентов','').replace('преподователей','').replace('курса','курс').replace('специальности ','').replace('09.02.07','программирование').replace('09.02.01','железо').replace(' класса','клс.').replace('после ','').replace('на','').replace('Информационные системы и программирование','программирование').replace('Компьютерные системы и комплексы','железо').replace(date,'').replace('  ', ' ').strip(),
#                     link=link,
#                     date=datetime.datetime(year=int(date.split('.')[2]),month=int(date.split('.')[1]),day=int(date.split('.')[0])),
#                     images=[], groups={})
#                 for i in result:
#                     if i.name == tt.name:
#                         result.remove(i)
#                 result.append(tt)
#                 async with sesion.get('https://ci.nsu.ru'+tt.link if not tt.link.startswith('https://') else tt.link, allow_redirects=True) as r:
#                     async with aiofiles.open(cfg.base_dir/'temp/pdf_files'/(tt.name+'.pdf'), 'wb') as file:
#                         await file.write(await r.read())
#                     doc = pymupdf.Document(cfg.base_dir/'temp/pdf_files'/(tt.name+'.pdf'))
#                     for page in doc:
#                         tt.text_content += page.get_text()
#     # DELETE ME
#     # result += [Timetable('1 спо TEST', '', datetime.datetime(2022, 3, 10), [], {'2401в2':[]})]
#     return sorted(result, key=lambda x: x.name)
#             ^ i wanna know if the guy who wrote this even understands it 🙏🙏

import os
import re
import aiohttp
import aiofiles
import pymupdf

from urllib.parse import unquote
from bs4 import BeautifulSoup as bs #<--- bullshit
from functools import reduce

from nautica.api import Config

from src.lib.schedule.Parser import delete_spaces

async def fetch_page(session: aiohttp.ClientSession, url: str) -> str:
    async with session.get(url, timeout=aiohttp.ClientTimeout(10)) as res:
        return await res.text()
    
def clean_filename(link: str, shorter_table: dict) -> str:
    #extract a clean timetable name from pdf link
    match = re.findall(r'\d\d.\d\d.\d\d', link)
    date = match[-1] if match else ""
    
    name = reduce(lambda x, y: x.replace(y, shorter_table[y]), shorter_table, link.split('/')[-1].replace(date, ''))
    return delete_spaces(name).strip()

async def download_pdf(session: aiohttp.ClientSession, url: str, save_path: str):
    async with session.get(url, allow_redirects=True) as resp:
        async with aiofiles.open(save_path, 'wb') as f:
            await f.write(await resp.read())

def prepare_temp_dir(path: str):
    os.makedirs(path, exist_ok=True)
    #remove old PDFs
    for f in os.listdir(path):
        os.remove(os.path.join(path, f))

async def download_timetables() -> list[dict]:
    #downloads all PDFs from ci.nsu.ru and extracts the text
    temp_dir = Config("vki")["schedules.pdfTemp"]
    prepare_temp_dir(temp_dir)

    result = []

    async with aiohttp.ClientSession(trust_env=True) as session:
        html_text = await fetch_page(session, 'https://ci.nsu.ru/education/schedule/')
        with open(f'{temp_dir}/page.html', 'w', encoding="utf-8") as f:
            f.write(html_text)

        soup = bs(html_text, 'html.parser')
        links = [unquote(a['href'].strip()) for a in soup.find_all('a', class_='file-link')]

        for link in links:
            if 'Основное' in link:
                continue

            tt_name = clean_filename(link, shorter_table)

            #remove duplicates
            # result = [r for r in result if r.name != tt_name]

            pdf_url = 'https://ci.nsu.ru' + link if not link.startswith('https://') else link
            pdf_path = f"{temp_dir}/{tt_name}.pdf"
            await download_pdf(session, pdf_url, pdf_path)
            
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