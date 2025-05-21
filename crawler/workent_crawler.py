# ### 5개씩 스크롤 내렸을 때
# import asyncio
# import time
# import urllib.parse
# import re
# import httpx
# from fastapi import FastAPI, Query
# from fastapi.responses import JSONResponse
# from bs4 import BeautifulSoup

# app = FastAPI()

# # 캐시 설정
# cache = {}
# CACHE_DURATION = 600  # 10분

# # 요청 헤더 (브라우저 위장)
# HEADERS = {
#     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
#     "Accept-Language": "ko-KR,ko;q=0.9",
#     "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9",
#     "Connection": "keep-alive"
# }

# # 모듈용 함수
# @app.get("/worknet/crawl")
# async def crawl_worknet_data(keyword: str, page: int, page_size: int) -> list:
#     now = time.time()
#     cache_key = f"{keyword}_{page}"

#     if cache_key in cache:
#         all_data, timestamp = cache[cache_key]
#         if now - timestamp < CACHE_DURATION:
#             start = (page - 1) * page_size % 20
#             end = start + page_size
#             return all_data[start:end]  # ✅ list로 반환
#     if cache_key in cache:
#         cache[cache_key] = (all_job_list, now)
#         if now - timestamp < CACHE_DURATION:
#             start = (page - 1) * page_size % 20
#             end = start + page_size
#             return all_job_list[start:end]
        
#     # 제외할 사이트 코드
#     EXCLUDE_SITE = "SAR"

#     # 포함할 사이트 코드 (SAR 제외)
#     SITE_CODES = [
#         "WORK", "GOJ", "ALI", "WIH", "CLE", "MMA", "CJK", "CIN", "CCN",
#         "OEW", "MIT", "CPR", "WFC", "IBK", "PRD", "KOS", "CAT", "CWT", "CDM"
#     ]

#     filtered_sites = ",".join(code for code in SITE_CODES if code != EXCLUDE_SITE)

        
#     encoded_keyword = urllib.parse.quote(keyword)
#     url = f"https://www.work24.go.kr/wk/a/b/1200/retriveDtlEmpSrchList.do?startCount=1&topQuerySearchArea=all&searchYn=Y&listCount=20&keyword=&srcKeyword={encoded_keyword}&programMenuIdentification=EBG020000000000&siteClcd={filtered_sites}"
#     async with httpx.AsyncClient(timeout=10.0, headers=HEADERS) as client:
#         try:
#             response = await client.get(url)
#             response.raise_for_status()
#         except httpx.RequestError as e:
#             return JSONResponse(content={"error": f"요청 실패: {str(e)}"}, status_code=500)

#         soup = BeautifulSoup(response.text, "html.parser")
#         job_sections = soup.select('div.box_table_wrap')

#         semaphore = asyncio.Semaphore(5)
#         tasks = [safe_process_job(client, job, semaphore) for job in job_sections[:20]]
#         all_job_list_nested = await asyncio.gather(*tasks)

#         # 각 작업이 list로 반환되므로 평탄화
#         all_job_list = [job for sublist in all_job_list_nested for job in sublist if job]

#     cache[cache_key] = (all_job_list, now)

#     start = (page - 1) * page_size % 20
#     end = start + page_size
#     return all_job_list[start:end]

# async def safe_process_job(client, job, semaphore):
#     async with semaphore:
#         return await process_single_job(client, job)

# async def process_single_job(client, job):
#     try:
#         company_names = job.find_all('a', class_='cp_name')
#         titles = job.find_all('a', class_='t3_sb')
#         img_tags = job.find_all('img')
#         salary_tags = job.find_all('span', class_='item b1_sb')
#         details_tags = job.find_all('span', class_='item sm')
#         location_tags = job.find_all('li', class_='site')
#         deadline_tags = job.find_all('td', class_='pd24')

#         if not company_names or not titles:
#             return []

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
#         return []   


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
    "Connection": "keep-alive",
    "Referer": "https://www.work24.go.kr/"
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

    # 제외할 사이트 코드
    EXCLUDE_SITE = "SAR"

    # 포함할 사이트 코드 (SAR 제외)
    SITE_CODES = [
        "WORK", "GOJ", "ALI", "WIH", "CLE", "MMA", "CJK", "CIN", "CCN",
        "OEW", "MIT", "CPR", "WFC", "IBK", "PRD", "KOS", "CAT", "CWT", "CDM"
    ]

    filtered_sites = ",".join(code for code in SITE_CODES if code != EXCLUDE_SITE)

    encoded_keyword = urllib.parse.quote(keyword)
    url = f"https://www.work24.go.kr/wk/a/b/1200/retriveDtlEmpSrchList.do?startCount=1&topQuerySearchArea=all&searchYn=Y&listCount=20&keyword=&srcKeyword={encoded_keyword}&programMenuIdentification=EBG020000000000&siteClcd={filtered_sites}"

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

            img_tag = img_tags[idx] if idx < len(img_tags) else None
            img_src = img_tag['src'].strip() if img_tag and 'src' in img_tag.attrs else "이미지 없음"
            if img_src != "이미지 없음" and not img_src.startswith("http"):
                img_src = "https://www.work24.go.kr" + img_src
            job_data["company_logo_url"] = img_src

            link_tag = title
            link = link_tag.get('href') if link_tag else ""
            full_link = urllib.parse.urljoin("https://www.work24.go.kr", link) if link else "정보 없음"
            job_data["details_url"] = full_link

            jobs.append(job_data)

        return jobs

    except Exception as e:
        print(f"Error processing job: {e}")
        return []

# 워크넷 상세 페이지 크롤링
async def crawl_worknet_detail(url: str) -> dict:
    try:
        async with httpx.AsyncClient(headers=HEADERS, timeout=10.0) as client:
            response = await client.get(url, follow_redirects=False)
            if response.status_code == 302:
                return {
                    "type": "error",
                    "content": "워크넷 접속이 차단되었습니다. 브라우저 환경에서 접속해주세요."
                }

            soup = BeautifulSoup(response.text, "html.parser")

            # iframe
            iframe = soup.find("iframe")
            if iframe and iframe.get("src"):
                iframe_src = iframe["src"]
                if not iframe_src.startswith("http"):
                    iframe_src = "https://www.work24.go.kr" + iframe_src
                return {"type": "iframe", "content": iframe_src}

            # 이미지
            images = soup.find_all("img")
            img_sources = [img["src"] for img in images if img.get("src")]
            if img_sources:
                return {"type": "image", "content": img_sources}

            # 텍스트/테이블
            text_blocks = soup.find_all(["div", "table"])
            content_text = "\n".join(block.get_text(strip=True) for block in text_blocks if block)
            if content_text:
                return {"type": "text", "content": content_text[:3000]}

            return {"type": "none", "content": "유효한 채용 상세 정보가 없습니다."}

    except Exception as e:
        return {
            "type": "error",
            "content": str(e)
        }


@app.get("/debug/worknet/iframe")
async def debug_worknet_iframe(iframe_url: str):
    try:
        async with httpx.AsyncClient(headers=HEADERS, timeout=10.0) as client:
            response = await client.get(iframe_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            preview = soup.get_text(strip=True)[:1000]
            return {
                "type": "preview",
                "length": len(preview),
                "preview": preview
            }
    except Exception as e:
        return {
            "type": "error",
            "message": str(e)
        }