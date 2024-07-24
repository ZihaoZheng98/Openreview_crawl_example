import os
import openreview
import re
from datetime import datetime
from tqdm import tqdm
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import requests
import os

def download_pdf_if_extraction_in_title(url, title, pdf_dir, keyword='Extraction'):
    if keyword in title:
        response = requests.get(url)
        with open(os.path.join(pdf_dir, f"{title}.pdf"), 'wb') as f:
            f.write(response.content)
# API V2
client = openreview.api.OpenReviewClient(
    baseurl='https://api2.openreview.net',
    username='zhengxiaoxiehit@gmail.com',
    password='GK5gtw6haJuN8cf'
)

def get_venue_ids(conference: str):
    """get conference venue id 

    Args:
        conference (str): conference name string. E.g. NeurIPS

    Returns:
        dict: {year: [list of venue ids for the year]}
    """
    venues = client.get_group(id='venues').members
    out = {}
    for v in venues:
        if '2024' not in v:
            continue
        name_list = v.split('/')
        name_search_result = [re.findall(f"^{conference}\.?.*", element) for element in name_list]
        if any(name_search_result):
            year_search_result = [re.findall(r'\d+', element) for element in name_list if len(re.findall(r'\d{4}', element)) == 1]
            if not year_search_result:
                continue
            assert len(year_search_result) == 1, f"{name_list} -> {year_search_result} | More than one numeric year found in venue name. e.g.: **/2022/**/2024"
            assert len(year_search_result[0]) == 1, f"{name_list} -> {year_search_result} | More than one numeric year found in venue name. e.g.: **/2022paper2024/**"

            year = year_search_result[0][0]
            if year not in out:
                out[year] = []
            out[year].append(v)
    return out

venue_ids = get_venue_ids("ACMMM")

submissions = []
submissions += client.get_all_notes(content={'venueid': 'acmmm.org/ACMMM/2024/Conference'})



# 创建一个文件，将这些论文列表存储在文件中
mm_oral_list = './mm_oral_list.txt'
mm_poster_list = './mm_poster_list.txt'
# save pdfs in ACMMM_pdfs
if not os.path.exists('ACMMM_pdfs'):
    os.makedirs('ACMMM_pdfs')
pdf_dir = 'ACMMM_pdfs'
o_fw = open(mm_oral_list,'w', encoding='utf-8')
p_fw = open(mm_poster_list,'w', encoding='utf-8')

for i, note in enumerate(tqdm(submissions)):
    #print("Title:", note.content['title'])
    venue = note.content['venue']
    pdfpath = 'https://openreview.net' +  note.content['pdf']['value']
    # get time for note and format to string
    if 'Oral' in venue['value']:
        o_fw.write("Title:" + note.content['title']['value']+ '\n')
    elif 'Poster' in venue['value']:
        p_fw.write("Title:" + note.content['title']['value']+ '\n')
    else:
        print(venue)
    # 如果title中包含extraction, 则下载pdf到pdf_dir中，文件名为title.pdf
    download_pdf_if_extraction_in_title(pdfpath, note.content['title']['value'], pdf_dir, 'Sarcasm')
    download_pdf_if_extraction_in_title(pdfpath, note.content['title']['value'], pdf_dir, 'Fake')
    download_pdf_if_extraction_in_title(pdfpath, note.content['title']['value'], pdf_dir, 'Named Entity')


o_fw.close()
p_fw.close()

# 'https://openreview.net/pdf/49c77cc7b9a37979289a59ddf8420c9685717749.pdf'
