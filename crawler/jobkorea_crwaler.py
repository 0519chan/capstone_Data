# import requests
# from bs4 import BeautifulSoup
# import urllib.parse
# import json
# # from selenium import webdriver
# # from selenium.webdriver.chrome.service import Service
# # from webdriver_manager.chrome import ChromeDriverManager
# import time

# # driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

# def crawl_job_data(keyword):
#     encoded_keyword = urllib.parse.quote(keyword)
#     url = f"https://www.jobkorea.co.kr/Search/?stext={encoded_keyword}&tabType=recruit&Page_No=1"
#     response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
#     soup = BeautifulSoup(response.text, "html.parser")
#     jobs = soup.select('article.list-item')
#     job_list = []
#     for job in jobs[:20]:
#         time.sleep(2)
#         try:
#             company_names = job.select_one('a.corp-name-link').text.strip()
#             job_title_element = job.select_one('a.information-title-link.dev-view')
#             if job_title_element:
#                 job_title = job_title_element.text.strip()
#                 link = urllib.parse.urljoin("https://www.jobkorea.co.kr", job_title_element['href'])
#                 full_link = urllib.parse.urljoin("https://www.jobkorea.co.kr", link)
#                 full_link = urllib.parse.quote(full_link, safe=':/&=?')
#             else:
#                 job_title = "제목 없음"
#                 link = None
#             job_info_list = []
#             job_info_ul = job.select_one('ul.chip-information-group')
#             if job_info_ul:
#                 job_info_items = job_info_ul.find_all('li', class_='chip-information-item')
#                 job_info_list = [item.text.strip() for item in job_info_items]
#             job_details = {}
#             # 상세페이지 크롤
#             if link:
#                 response_detail = requests.get(link, headers={'User-Agent': 'Mozilla/5.0'})
#                 response_detail.raise_for_status()
#                 soup_detail = BeautifulSoup(response_detail.text, "html.parser")
#                 qualification_info = {tag.text.strip(): value.text.strip().replace('\n', '').replace('\r', '').replace('\t', '').replace(' ', '') for tag, value in zip(soup_detail.select('div.tbCol')[0].select('dt'), soup_detail.select('div.tbCol')[0].select('dd'))}
#                 employment_info = {tag.text.strip(): value.text.strip().replace('\n', '').replace('\r', '').replace('\t', '').replace(' ', '') for tag, value in zip(soup_detail.select('div.tbCol')[1].select('dt'), soup_detail.select('div.tbCol')[1].select('dd'))}
#                 company_info = {tag.text.strip(): value.text.strip().replace('\n', '').replace('\r', '').replace('\t', '').replace(' ', '') for tag, value in zip(soup_detail.select('div.tbCol')[2].select('dt'), soup_detail.select('div.tbCol')[2].select('dd'))}

#                 # 이미지 src 추출 및 JSON 형태로 추가
#                 img_tag = soup_detail.find('img', id='cologo')
#                 if img_tag and 'src' in img_tag.attrs:
#                     src_value = img_tag['src'].strip()
#                     company_info["company_img_src"] = src_value
#                 else:
#                     company_info["company_img_src"] = "이미지 없음"

#                 job_details = {
#                     "qualification": qualification_info,
#                     "employment": employment_info,
#                     "company": company_info,
#                 }
#             job_data = {
#                 "company_name": company_names,
#                 "title": job_title,
#                 "link": full_link,
#                 "info": job_info_list,
#                 "details": job_details
#             }
#             job_list.append(job_data)#
#         except Exception as e:
#             print(f"Error processing job: {e}")
#     return job_list

# keyword = '데이터 분석'
# job_data_list = crawl_job_data(keyword)
# json_result = json.dumps(job_data_list, ensure_ascii=False, indent=4)
# print(json_result)


# 이거 진짜
# import requests
# from bs4 import BeautifulSoup
# import urllib.parse
# import json
# import time

# def crawl_job_data(keyword):
#     encoded_keyword = urllib.parse.quote(keyword)
#     url = f"https://www.jobkorea.co.kr/Search/?stext={encoded_keyword}&tabType=recruit&Page_No=1"
#     response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
#     soup = BeautifulSoup(response.text, "html.parser")
#     jobs = soup.select('article.list-item')
#     job_list = []
    
#     for job in jobs[:20]:
#         time.sleep(1)
#         try:
#             company_name = job.select_one('a.corp-name-link').text.strip()
#             job_title_element = job.select_one('a.information-title-link.dev-view')

#             if job_title_element:
#                 job_title = job_title_element.text.strip()
#                 link = urllib.parse.urljoin("https://www.jobkorea.co.kr", job_title_element['href'])
#                 detail_url = urllib.parse.quote(link, safe=':/&=?')
#             else:
#                 job_title = "제목 없음"
#                 detail_url = None

#             job_info_list = []
#             job_info_ul = job.select_one('ul.chip-information-group')

#             if job_info_ul:
#                 job_info_items = job_info_ul.find_all('li', class_='chip-information-item')
#                 job_info_list = [item.text.strip() for item in job_info_items]

#             salary = next((info for info in job_info_list if '만원' in info or '회사내규' in info), "협의 가능")
#             career_level = next((info for info in job_info_list if '경력' in info or '신입' in info), "경력 무관")
#             education_level = next((info for info in job_info_list if '학력' in info or '고졸' in info or '대졸' in info), "학력 무관")
#             location = next((info for info in job_info_list if '서울' in info or '경기' in info or '부산' in info), "지역 미정")

#             company_logo_url = "이미지 없음"
#             if detail_url:
#                 response_detail = requests.get(detail_url, headers={'User-Agent': 'Mozilla/5.0'})
#                 soup_detail = BeautifulSoup(response_detail.text, "html.parser")

#                 img_tag = soup_detail.find('img', id='cologo')
#                 if img_tag and 'src' in img_tag.attrs:
#                     company_logo_url = img_tag['src'].strip()

#             job_data = {
#                 "company_name": company_name,
#                 "title": job_title,
#                 "salary": salary,
#                 "career_level": career_level,
#                 "education_level": education_level,
#                 "location": location,
#                 "company_logo_url": company_logo_url,
#                 "detail_url": detail_url
#             }
#             job_list.append(job_data)

#         except Exception as e:
#             print(f"Error processing job: {e}")

#     return job_list

# keyword = '데이터 분석'
# job_data_list = crawl_job_data(keyword)
# json_result = json.dumps(job_data_list, ensure_ascii=False, indent=4)
# print(json_result)

import asyncio
import httpx
from bs4 import BeautifulSoup
import urllib.parse
import json
import time

# 메모리 캐시
cache = {}
CACHE_DURATION = 300  # 5분

async def crawl_job_data_async(keyword):
    now = time.time()

    # 캐시가 있고 만료 안 됐으면 리턴
    if keyword in cache:
        data, timestamp = cache[keyword]
        if now - timestamp < CACHE_DURATION:
            return data

    encoded_keyword = urllib.parse.quote(keyword)
    url = f"https://www.jobkorea.co.kr/Search/?stext={encoded_keyword}&tabType=recruit&Page_No=1"

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(response.text, "html.parser")
        jobs = soup.select('article.list-item')

        tasks = []
        for job in jobs[:20]:  # 20개만
            tasks.append(process_single_job(client, job))

        job_list = await asyncio.gather(*tasks)

    # 크롤링 완료 후 캐시 저장
    cache[keyword] = (job_list, now)
    return job_list

async def process_single_job(client, job):
    try:
        company_name = job.select_one('a.corp-name-link').text.strip()
        job_title_element = job.select_one('a.information-title-link.dev-view')

        if job_title_element:
            job_title = job_title_element.text.strip()
            link = urllib.parse.urljoin("https://www.jobkorea.co.kr", job_title_element['href'])
            detail_url = urllib.parse.quote(link, safe=':/&=?')
        else:
            job_title = "제목 없음"
            detail_url = None

        job_info_list = []
        job_info_ul = job.select_one('ul.chip-information-group')
        if job_info_ul:
            job_info_items = job_info_ul.find_all('li', class_='chip-information-item')
            job_info_list = [item.text.strip() for item in job_info_items]

        salary = next((info for info in job_info_list if '만원' in info or '회사내규' in info), "협의 가능")
        career_level = next((info for info in job_info_list if '경력' in info or '신입' in info), "경력 무관")
        education_level = next((info for info in job_info_list if '학력' in info or '고졸' in info or '대졸' in info), "학력 무관")
        location = next((info for info in job_info_list if '서울' in info or '경기' in info or '부산' in info), "지역 미정")

        company_logo_url = "이미지 없음"
        if detail_url:
            try:
                response_detail = await client.get(detail_url, headers={'User-Agent': 'Mozilla/5.0'})
                soup_detail = BeautifulSoup(response_detail.text, "html.parser")
                img_tag = soup_detail.find('img', id='cologo')
                if img_tag and 'src' in img_tag.attrs:
                    company_logo_url = img_tag['src'].strip()
            except Exception as e:
                print(f"Error loading detail page: {e}")

        return {
            "company_name": company_name,
            "title": job_title,
            "salary": salary,
            "career_level": career_level,
            "education_level": education_level,
            "location": location,
            "company_logo_url": company_logo_url,
            "detail_url": detail_url
        }

    except Exception as e:
        print(f"Error processing job: {e}")
        return {}

# 실행용 메인 함수
async def main():
    keyword = '데이터 분석'
    job_data_list = await crawl_job_data_async(keyword)
    json_result = json.dumps(job_data_list, ensure_ascii=False, indent=4)
    print(json_result)

# 바로 실행
if __name__ == "__main__":
    asyncio.run(main())