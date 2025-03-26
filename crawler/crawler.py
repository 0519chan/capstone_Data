import requests
from bs4 import BeautifulSoup
import urllib.parse
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

def crawl_job_data(keyword):
    encoded_keyword = urllib.parse.quote(keyword)
    url = f"https://www.jobkorea.co.kr/Search/?stext={encoded_keyword}&tabType=recruit&Page_No=1"
    response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
    soup = BeautifulSoup(response.text, "html.parser")
    jobs = soup.select('article.list-item')
    job_list = []
    for job in jobs[:20]:
        time.sleep(2)
        try:
            company_names = job.select_one('a.corp-name-link').text.strip()
            job_title_element = job.select_one('a.information-title-link.dev-view')
            if job_title_element:
                job_title = job_title_element.text.strip()
                link = urllib.parse.urljoin("https://www.jobkorea.co.kr", job_title_element['href'])
                full_link = urllib.parse.urljoin("https://www.jobkorea.co.kr", link)
                full_link = urllib.parse.quote(full_link, safe=':/&=?')
            else:
                job_title = "제목 없음"
                link = None
            job_info_list = []
            job_info_ul = job.select_one('ul.chip-information-group')
            if job_info_ul:
                job_info_items = job_info_ul.find_all('li', class_='chip-information-item')
                job_info_list = [item.text.strip() for item in job_info_items]
            job_details = {}
            # 상세페이지 크롤
            if link:
                response_detail = requests.get(link, headers={'User-Agent': 'Mozilla/5.0'})
                response_detail.raise_for_status()
                soup_detail = BeautifulSoup(response_detail.text, "html.parser")
                qualification_info = {tag.text.strip(): value.text.strip().replace('\n', '').replace('\r', '').replace('\t', '').replace(' ', '') for tag, value in zip(soup_detail.select('div.tbCol')[0].select('dt'), soup_detail.select('div.tbCol')[0].select('dd'))}
                employment_info = {tag.text.strip(): value.text.strip().replace('\n', '').replace('\r', '').replace('\t', '').replace(' ', '') for tag, value in zip(soup_detail.select('div.tbCol')[1].select('dt'), soup_detail.select('div.tbCol')[1].select('dd'))}
                company_info = {tag.text.strip(): value.text.strip().replace('\n', '').replace('\r', '').replace('\t', '').replace(' ', '') for tag, value in zip(soup_detail.select('div.tbCol')[2].select('dt'), soup_detail.select('div.tbCol')[2].select('dd'))}

                # 이미지 src 추출 및 JSON 형태로 추가
                img_tag = soup_detail.find('img', id='cologo')
                if img_tag and 'src' in img_tag.attrs:
                    src_value = img_tag['src'].strip()
                    company_info["company_img_src"] = src_value
                else:
                    company_info["company_img_src"] = "이미지 없음"

                job_details = {
                    "qualification": qualification_info,
                    "employment": employment_info,
                    "company": company_info,
                }
            job_data = {
                "company_name": company_names,
                "title": job_title,
                "link": full_link,
                "info": job_info_list,
                "details": job_details
            }
            job_list.append(job_data)
        except Exception as e:
            print(f"Error processing job: {e}")
    return job_list

keyword = '데이터 분석'
job_data_list = crawl_job_data(keyword)
json_result = json.dumps(job_data_list, ensure_ascii=False, indent=4)
print(json_result)          