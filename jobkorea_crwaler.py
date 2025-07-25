### 세부페이지 크롤링

import asyncio
import time
import urllib.parse
import httpx
from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from bs4 import BeautifulSoup

app = FastAPI()

# 캐시 설정
cache = {}
image_cache = {}
CACHE_DURATION = 600  # 10분

# 요청 헤더
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Accept-Language": "ko-KR,ko;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9",
    "Connection": "keep-alive"
}

# @app.get("/crawl")
# async def crawl_job_data_async(
#     keyword: str = Query('데이터분석', description="검색할 키워드"),
#     page: int = Query(1, description="jobkorea 페이지 번호 (1부터 시작)"),
#     page_size: int = Query(5, description="한 번에 몇 개 보여줄지")
# ):
#     now = time.time()
#     cache_key = f"{keyword}_{page}"

#     # 캐시 확인
#     if cache_key in cache:
#         all_data, timestamp = cache[cache_key]
#         if now - timestamp < CACHE_DURATION:
#             start = (page - 1) * page_size % 20
#             end = start + page_size
#             return all_data[start:end]

#     # URL 생성
#     encoded_keyword = urllib.parse.quote(keyword)
#     url = f"https://www.jobkorea.co.kr/Search/?stext={encoded_keyword}&tabType=recruit&Page_No={page}"

#     async with httpx.AsyncClient(timeout=10.0, headers=HEADERS) as client:
#         try:
#             response = await client.get(url)
#             response.raise_for_status()
#         except httpx.RequestError as e:
#             return JSONResponse(content={"error": f"요청 실패: {str(e)}"}, status_code=500)

#         soup = BeautifulSoup(response.text, "html.parser")
#         jobs = soup.select('article.list-item')

#         # 세마포어 설정
#         semaphore = asyncio.Semaphore(5)
#         tasks = [safe_process_job(client, job, semaphore) for job in jobs[:20]]
#         all_job_list = await asyncio.gather(*tasks)

#     # 캐시 저장
#     cache[cache_key] = (all_job_list, now)

#     start = (page - 1) * page_size % 20
#     end = start + page_size
#     return all_job_list[start:end]
@app.get("/crawl")
async def crawl_job_data_async(
    keyword: str = Query('데이터분석', description="검색할 키워드"),
    page: int = Query(1, description="jobkorea 페이지 번호 (1부터 시작)"),
    page_size: int = Query(5, description="한 번에 몇 개 보여줄지")
):
    now = time.time()
    cache_key = f"{keyword}_{page}"

    # 캐시 확인
    if cache_key in cache:
        all_data, timestamp = cache[cache_key]
        if now - timestamp < CACHE_DURATION:
            print(f"[CACHE HIT] {cache_key}")
            start = (page - 1) * page_size % 20
            end = start + page_size
            return all_data[start:end]

    # URL 생성
    encoded_keyword = urllib.parse.quote(keyword)
    url = f"https://www.jobkorea.co.kr/Search/?stext={encoded_keyword}&tabType=recruit&Page_No={page}"

    async with httpx.AsyncClient(timeout=10.0, headers=HEADERS) as client:
        try:
            print(f"[REQUEST] URL: {url}")
            response = await client.get(url)
            print(f"[RESPONSE] Status: {response.status_code}")
            print(f"[RESPONSE] Content length: {len(response.text)}")
            with open("jobkorea_debug.html", "w", encoding="utf-8") as f:
             f.write(response.text)

            response.raise_for_status()
        except httpx.RequestError as e:
            print(f"[ERROR] 요청 실패: {e}")
            return JSONResponse(content={"error": f"요청 실패: {str(e)}"}, status_code=500)

        soup = BeautifulSoup(response.text, "html.parser")
        jobs = soup.select('article.list-item')

        print(f"[PARSE] 잡 공고 개수: {len(jobs)}")

        # 세마포어 설정
        semaphore = asyncio.Semaphore(5)
        tasks = [safe_process_job(client, job, semaphore) for job in jobs[:20]]
        all_job_list = await asyncio.gather(*tasks)

    # 캐시 저장
    cache[cache_key] = (all_job_list, now)

    start = (page - 1) * page_size % 20
    end = start + page_size
    return all_job_list[start:end]

async def safe_process_job(client, job, semaphore):
    async with semaphore:
        return await process_single_job(client, job)

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

        # 상세 페이지에서 추가 정보 크롤링
        details = {}
        company_logo_url = "이미지 없음"

        if detail_url:
            if detail_url in image_cache:
                company_logo_url = image_cache[detail_url]
            else:
                try:
                    response_detail = await client.get(detail_url, headers=HEADERS)
                    soup_detail = BeautifulSoup(response_detail.text, "html.parser")

                    divs = soup_detail.select('div.tbCol')
                    if len(divs) >= 3:
                        qualification_info = {dt.text.strip(): dd.text.strip() for dt, dd in zip(divs[0].select('dt'), divs[0].select('dd'))}
                        employment_info = {dt.text.strip(): dd.text.strip() for dt, dd in zip(divs[1].select('dt'), divs[1].select('dd'))}
                        company_info = {dt.text.strip(): dd.text.strip() for dt, dd in zip(divs[2].select('dt'), divs[2].select('dd'))}
                    else:
                        qualification_info = {}
                        employment_info = {}
                        company_info = {}

                    img_tag = soup_detail.find('img', id='cologo')
                    if img_tag and 'src' in img_tag.attrs:
                        company_logo_url = img_tag['src'].strip()
                        image_cache[detail_url] = company_logo_url

                    company_info['company_logo_url'] = company_logo_url

                    details = {
                        "qualification": qualification_info,
                        "employment": employment_info,
                        "company": company_info
                    }

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
            "detail_url": detail_url,
            "details": details
        }

    except Exception as e:
        print(f"Error processing job: {e}")
        return {"error": str(e)}

async def crawl_job_detail_async(url: str) -> dict:
    try:
        async with httpx.AsyncClient(headers=HEADERS, timeout=10.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            iframe = soup.find("iframe", {"id": "gib_frame"})
            if iframe and iframe.get("src"):
                iframe_src = iframe["src"]
                iframe_url = "https://www.jobkorea.co.kr" + iframe_src

                iframe_response = await client.get(iframe_url)
                iframe_soup = BeautifulSoup(iframe_response.text, "html.parser")

                # 텍스트 추출
                text_content = iframe_soup.get_text(separator="\n", strip=True)[:3000]

                # 이미지 추출
                img_tags = iframe_soup.find_all("img")
                image_urls = []
                for img in img_tags:
                    src = img.get("src")
                    if src:
                        full_url = src if src.startswith("http") else "https://www.jobkorea.co.kr" + src
                        image_urls.append(full_url)

                return {
                    "type": "mixed",
                    "content": {
                        "text": text_content,
                        "images": image_urls
                    }
                }
            else:
                return {
                    "type": "none",
                    "content": "iframe 또는 상세 정보가 존재하지 않습니다."
                }

    except Exception as e:
        return {
            "type": "error",
            "content": str(e)
        }
async def debug_detail(url: str):
    return {
        "type": "debug",
        "url": url,
        "message": "디버그용 상세 분석 완료"
    }