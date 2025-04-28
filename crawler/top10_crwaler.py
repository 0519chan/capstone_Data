# import asyncio
# import httpx
# from bs4 import BeautifulSoup
# import urllib.parse
# import json
# import time


# BASE_URL = "https://www.jobkorea.co.kr"
# TOP100_URL = f"{BASE_URL}/top100/"
# HEADERS = {'User-Agent': 'Mozilla/5.0'}

# # 메모리 캐시
# cache = {}
# CACHE_DURATION = 600  # 10분


# async def crawl_top100_data_async():
#     now = time.time()

#     # 캐시 확인
#     if 'top100' in cache:
#         data, timestamp = cache['top100']
#         if now - timestamp < CACHE_DURATION:
#             return data

#     async with httpx.AsyncClient(timeout=10.0) as client:
#         response = await client.get(TOP100_URL, headers=HEADERS)
#         soup = BeautifulSoup(response.text, "html.parser")
#         main = soup.select('div.rankListArea.devSarterTab')

#         tasks = []

#         for list_area in main:
#             tags = list_area.find_all('li')
#             for info in tags:
#                 tasks.append(process_single_company(client, info))

#         data_list = await asyncio.gather(*tasks)

#     # 캐시 저장
#     cache['top100'] = (data_list, now)
#     return data_list

# NEED_KEYS = ["경력", "고용형태", "급여", "지역", "시간"]

# async def process_single_company(client, info):
#     try:
#         company = info.find('a', 'coLink')
#         company_name = company.text.strip()
#         company_link = urllib.parse.urljoin(BASE_URL, company.get('href'))
#         rank = info.find('span', 'num').text.strip()

#         title_tag = info.find('a', 'link')
#         title = title_tag.text.strip()
#         detail_url = urllib.parse.urljoin(BASE_URL, title_tag.get('href'))

#         job_info = info.find('div', 'sTit').text.strip()
#         job_requirements = info.find('div', 'sDsc').text.strip()

#         deadline_tag = info.find('span', 'day')
#         deadline = deadline_tag.text.strip() if deadline_tag else "상시채용"

#         extra_info = {}
#         if detail_url:
#             try:
#                 response_detail = await client.get(detail_url, headers=HEADERS)
#                 soup_detail = BeautifulSoup(response_detail.text, "html.parser")
#                 details = soup_detail.select('dl.tbList')
#                 for dl in details:
#                     dt_tags = dl.find_all('dt')
#                     dd_tags = dl.find_all('dd')
#                     for dt, dd in zip(dt_tags, dd_tags):
#                         key = dt.get_text(strip=True)
#                         value = dd.get_text(separator=" ", strip=True)
#                         extra_info[key] = value
#                 # 여기서 필터링
#                 extra_info = {k: v for k, v in extra_info.items() if k in NEED_KEYS}
#             except Exception as e:
#                 print(f"Error loading detail page: {e}")

#         return {
#             "rank": rank,
#             "company_name": company_name,
#             "company_link": company_link,
#             "title": title,
#             "detail_url": detail_url,
#             "job_info": job_info,
#             "job_requirements": job_requirements,
#             "deadline": deadline,
#             "extra_info": extra_info
#         }

#     except Exception as e:
#         print(f"Error processing company: {e}")
#         return {}

# async def main():
#     data_list = await crawl_top100_data_async()
#     print(json.dumps(data_list, ensure_ascii=False, indent=4))

# if __name__ == "__main__":
#     asyncio.run(main())

import asyncio
import time
import json
import urllib.parse

import httpx
from bs4 import BeautifulSoup
from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI()

BASE_URL = "https://www.jobkorea.co.kr"
TOP100_URL = f"{BASE_URL}/top100/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Connection": "keep-alive"
    }

CACHE_FILE = "top100_cache.json"
CACHE_DURATION = 86400  # 24시간
NEED_KEYS = ["경력", "고용형태", "급여", "지역", "시간"]

# 메모리 캐시 초기화
cache = {}

async def crawl_top100_data_async():
    now = time.time()

    # 캐시가 유효하면 메모리 데이터 반환
    if 'top100' in cache:
        data, timestamp = cache['top100']
        if now - timestamp < CACHE_DURATION:
            return data

    # 새로 크롤링
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(TOP100_URL, headers=HEADERS)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        main = soup.select('div.rankListArea.devSarterTab')

        tasks = []
        for list_area in main:
            tags = list_area.find_all('li')
            for info in tags:
                tasks.append(process_single_company(client, info))

        data_list = await asyncio.gather(*tasks)

    # 캐시에 저장
    cache['top100'] = (data_list, now)

    # 파일에도 저장 (백업용)
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(data_list, f, ensure_ascii=False, indent=4)

    return data_list

async def process_single_company(client, info):
    try:
        company = info.find('a', 'coLink')
        company_name = company.text.strip()
        company_link = urllib.parse.urljoin(BASE_URL, company.get('href'))
        rank = info.find('span', 'num').text.strip()

        title_tag = info.find('a', 'link')
        title = title_tag.text.strip()
        detail_url = urllib.parse.urljoin(BASE_URL, title_tag.get('href'))

        job_info = info.find('div', 'sTit').text.strip()
        job_requirements = info.find('div', 'sDsc').text.strip()

        deadline_tag = info.find('span', 'day')
        deadline = deadline_tag.text.strip() if deadline_tag else "상시채용"

        extra_info = {}
        if detail_url:
            try:
                response_detail = await client.get(detail_url, headers=HEADERS)
                soup_detail = BeautifulSoup(response_detail.text, "html.parser")
                details = soup_detail.select('dl.tbList')
                for dl in details:
                    dt_tags = dl.find_all('dt')
                    dd_tags = dl.find_all('dd')
                    for dt, dd in zip(dt_tags, dd_tags):
                        key = dt.get_text(strip=True)
                        value = dd.get_text(separator=" ", strip=True)
                        extra_info[key] = value
                # 필요한 키만 남기기
                extra_info = {k: v for k, v in extra_info.items() if k in NEED_KEYS}
            except Exception as e:
                print(f"Error loading detail page: {e}")

        return {
            "rank": rank,
            "company_name": company_name,
            "company_link": company_link,
            "title": title,
            "detail_url": detail_url,
            "job_info": job_info,
            "job_requirements": job_requirements,
            "deadline": deadline,
            "extra_info": extra_info
        }

    except Exception as e:
        print(f"Error processing company: {e}")
        return {}




