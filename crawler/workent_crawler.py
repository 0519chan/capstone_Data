# import asyncio
# import time
# import urllib.parse
# import httpx
# from fastapi import FastAPI, Query
# from fastapi.responses import JSONResponse
# from bs4 import BeautifulSoup
# import json
# import re

# app = FastAPI()

# # 메모리 캐시
# cache = {}
# CACHE_DURATION = 600  # 10분

# async def crawl_job_data_async(keyword):
#     now = time.time()

#     # 캐시가 있고 만료 안 됐으면 리턴
#     if keyword in cache:
#         data, timestamp = cache[keyword]
#         if now - timestamp < CACHE_DURATION:
#             return data

#     encoded_keyword = urllib.parse.quote(keyword)
#     url = f"https://www.work24.go.kr/wk/a/b/1200/retriveDtlEmpSrchList.do?startCount=1&topQuerySearchArea=all&searchYn=Y&listCount=20&keyword=&srcKeyword={encoded_keyword}&programMenuIdentification=EBG020000000000"

#     async with httpx.AsyncClient(timeout=10.0) as client:
#         try:
#             response = await client.get(url, headers={'User-Agent': 'Mozilla/5.0'})
#             response.raise_for_status()
#         except httpx.RequestError as e:
#             return {"error": f"요청 실패: {str(e)}"}

#         soup = BeautifulSoup(response.text, "html.parser")
#         job_sections = soup.select('div.box_table_wrap')

#         tasks = []
#         for job in job_sections[:20]:  # 20개만
#             tasks.append(process_single_job(job))

#         all_jobs = await asyncio.gather(*tasks)

#         # 결과 정리
#         job_list = [job for job in all_jobs if job]  # 빈 dict 제외

#     # 캐시에 저장
#     cache[keyword] = (job_list, now)
#     return job_list

# async def process_single_job(job):
#     try:
#         company_names = job.find_all('a', class_='cp_name')
#         titles = job.find_all('a', class_='t3_sb')
#         img_tags = job.find_all('img')
#         salary_tags = job.find_all('span', class_='item b1_sb')
#         details_tags = job.find_all('span', class_='item sm')
#         location_tags = job.find_all('li', class_='site')
#         deadline_tags = job.find_all('td', class_='pd24')

#         if not company_names or not titles:
#             return {}

#         dedadline_texts = []
#         for deadline_info in deadline_tags:
#             deadline_info_tags = deadline_info.find_all('p', class_='s1_r')
#             for tag in deadline_info_tags:
#                 text = tag.get_text(strip=True)
#                 if '마감일 :' in text:
#                     dedadline_texts.append(text.replace('마감일 :', '').strip())
#                 else:
#                     dedadline_texts.append("마감시까지 채용")

#         jobs = []
#         for idx, (company, title) in enumerate(zip(company_names, titles)):
#             raw_salary = salary_tags[idx].get_text(strip=True) if idx < len(salary_tags) else "정보 없음"
#             clean_salary = re.sub(r'[\r\n\t\s]', '', raw_salary)

#             salary_match = re.search(r'(\d[\d,]*)', clean_salary)
#             if salary_match:
#                 clean_salary = f"연봉 {salary_match.group(1)}원"

#             deadline = dedadline_texts[idx] if idx < len(dedadline_texts) else "정보 없음"

#             job_data = {
#                 "company_name": company.text.strip(),
#                 "title": title.text.strip(),
#                 "salary": clean_salary,
#                 "career_level": details_tags[idx * 2].get_text(strip=True) if idx * 2 < len(details_tags) else "정보 없음",
#                 "education_level": details_tags[idx * 2 + 1].get_text(strip=True) if idx * 2 + 1 < len(details_tags) else "정보 없음",
#                 "location": location_tags[idx].get_text(strip=True) if idx < len(location_tags) else "정보 없음",
#                 "company_logo_url": "이미지 없음",
#                 "details_url": "",
#                 "deadline": deadline
#             }

#             # 회사 로고 이미지
#             img_tag = img_tags[idx] if idx < len(img_tags) else None
#             img_src = img_tag['src'].strip() if img_tag and 'src' in img_tag.attrs else "이미지 없음"
#             if img_src != "이미지 없음" and not img_src.startswith("http"):
#                 img_src = "https://www.work24.go.kr" + img_src
#             job_data["company_logo_url"] = img_src

#             # 상세 페이지 링크
#             link_tag = title
#             link = link_tag.get('href') if link_tag else ""
#             full_link = urllib.parse.urljoin("https://www.work24.go.kr", link) if link else "정보 없음"
#             job_data["details_url"] = full_link

#             jobs.append(job_data)

#         return jobs

#     except Exception as e:
#         print(f"Error processing job: {e}")
#         return {}

# # 메인 함수
# async def main():
#     keyword = '데이터 분석'
#     job_data_list = await crawl_job_data_async(keyword)
#     json_result = json.dumps(job_data_list, ensure_ascii=False, indent=4)
#     print(json_result)

# if __name__ == "__main__":
#     asyncio.run(main())




### 5개씩 스크롤 내렸을 때
import asyncio
import time
import urllib.parse
import re
import httpx
from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from bs4 import BeautifulSoup

app = FastAPI()

# 캐시 설정
cache = {}
CACHE_DURATION = 600  # 10분

# 요청 헤더 (브라우저 위장)
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Accept-Language": "ko-KR,ko;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9",
    "Connection": "keep-alive"
}

# 모듈용 함수
@app.get("/worknet/crawl")
async def crawl_worknet_data(keyword: str, page: int, page_size: int) -> list:
    now = time.time()
    cache_key = f"{keyword}_{page}"

    if cache_key in cache:
        all_data, timestamp = cache[cache_key]
        if now - timestamp < CACHE_DURATION:
            start = (page - 1) * page_size % 20
            end = start + page_size
            return all_data[start:end]  # ✅ list로 반환
    if cache_key in cache:
        cache[cache_key] = (all_job_list, now)
        if now - timestamp < CACHE_DURATION:
            start = (page - 1) * page_size % 20
            end = start + page_size
            return all_job_list[start:end]
        
    encoded_keyword = urllib.parse.quote(keyword)
    url = f"https://www.work24.go.kr/wk/a/b/1200/retriveDtlEmpSrchList.do?startCount=1&topQuerySearchArea=all&searchYn=Y&listCount=20&keyword=&srcKeyword={encoded_keyword}&programMenuIdentification=EBG020000000000"

    async with httpx.AsyncClient(timeout=10.0, headers=HEADERS) as client:
        try:
            response = await client.get(url)
            response.raise_for_status()
        except httpx.RequestError as e:
            return JSONResponse(content={"error": f"요청 실패: {str(e)}"}, status_code=500)

        soup = BeautifulSoup(response.text, "html.parser")
        job_sections = soup.select('div.box_table_wrap')

        semaphore = asyncio.Semaphore(5)
        tasks = [safe_process_job(client, job, semaphore) for job in job_sections[:20]]
        all_job_list_nested = await asyncio.gather(*tasks)

        # 각 작업이 list로 반환되므로 평탄화
        all_job_list = [job for sublist in all_job_list_nested for job in sublist if job]

    cache[cache_key] = (all_job_list, now)

    start = (page - 1) * page_size % 20
    end = start + page_size
    return all_job_list[start:end]

async def safe_process_job(client, job, semaphore):
    async with semaphore:
        return await process_single_job(client, job)

async def process_single_job(client, job):
    try:
        company_names = job.find_all('a', class_='cp_name')
        titles = job.find_all('a', class_='t3_sb')
        img_tags = job.find_all('img')
        salary_tags = job.find_all('span', class_='item b1_sb')
        details_tags = job.find_all('span', class_='item sm')
        location_tags = job.find_all('li', class_='site')
        deadline_tags = job.find_all('td', class_='pd24')

        if not company_names or not titles:
            return []

        dedadline_texts = []
        for deadline_info in deadline_tags:
            deadline_info_tags = deadline_info.find_all('p', class_='s1_r')
            for tag in deadline_info_tags:
                text = tag.get_text(strip=True)
                if '마감일 :' in text:
                    dedadline_texts.append(text.replace('마감일 :', '').strip())
                else:
                    dedadline_texts.append("마감시까지 채용")

        jobs = []
        for idx, (company, title) in enumerate(zip(company_names, titles)):
            raw_salary = salary_tags[idx].get_text(strip=True) if idx < len(salary_tags) else "정보 없음"
            clean_salary = re.sub(r'[\r\n\t\s]', '', raw_salary)
            salary_match = re.search(r'(\d[\d,]*)', clean_salary)
            if salary_match:
                clean_salary = f"연봉 {salary_match.group(1)}원"

            deadline = dedadline_texts[idx] if idx < len(dedadline_texts) else "정보 없음"

            job_data = {
                "company_name": company.text.strip(),
                "title": title.text.strip(),
                "salary": clean_salary,
                "career_level": details_tags[idx * 2].get_text(strip=True) if idx * 2 < len(details_tags) else "정보 없음",
                "education_level": details_tags[idx * 2 + 1].get_text(strip=True) if idx * 2 + 1 < len(details_tags) else "정보 없음",
                "location": location_tags[idx].get_text(strip=True) if idx < len(location_tags) else "정보 없음",
                "company_logo_url": "이미지 없음",
                "details_url": "",
                "deadline": deadline
            }

            # 회사 로고 이미지
            img_tag = img_tags[idx] if idx < len(img_tags) else None
            img_src = img_tag['src'].strip() if img_tag and 'src' in img_tag.attrs else "이미지 없음"
            if img_src != "이미지 없음" and not img_src.startswith("http"):
                img_src = "https://www.work24.go.kr" + img_src
            job_data["company_logo_url"] = img_src

            # 상세 페이지 링크
            link_tag = title
            link = link_tag.get('href') if link_tag else ""
            full_link = urllib.parse.urljoin("https://www.work24.go.kr", link) if link else "정보 없음"
            job_data["details_url"] = full_link

            jobs.append(job_data)

        return jobs

    except Exception as e:
        print(f"Error processing job: {e}")
        return []