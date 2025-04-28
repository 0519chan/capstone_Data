import asyncio
import time
import re
import urllib.parse
import json
import httpx
from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from bs4 import BeautifulSoup

app = FastAPI()

# 메모리 캐시
cache = {}
CACHE_DURATION = 300  # 5분

@app.get("/crawl")
async def crawl_job_data_async(
    keyword: str = Query('데이터분석', description="검색할 키워드"),
    page: int = Query(2,  description="페이지 번호 (기본 1페이지)")
):
    now = time.time()

    if (keyword, page) in cache:
        data, timestamp = cache[(keyword, page)]
        if now - timestamp < CACHE_DURATION:
            return JSONResponse(content=data)

    encoded_keyword = urllib.parse.quote(keyword)
    start_count = (page - 1) * 20 + 1
    url = f"https://www.work24.go.kr/wk/a/b/1200/retriveDtlEmpSrchList.do?startCount={start_count}&topQuerySearchArea=all&searchYn=Y&listCount=20&keyword=&srcKeyword={encoded_keyword}&programMenuIdentification=EBG020000000000"

    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(url, headers={'User-Agent': 'Mozilla/5.0'})
            response.raise_for_status()
        except httpx.RequestError as e:
            return JSONResponse(content={"error": f"요청 실패: {str(e)}"}, status_code=500)

        soup = BeautifulSoup(response.text, "html.parser")
        job_sections = soup.select('div.box_table_wrap')

        tasks = [process_single_job(job) for job in job_sections]
        all_jobs = await asyncio.gather(*tasks)
        job_list = [job for job in all_jobs if job]  # 빈 dict 제외

    cache[(keyword, page)] = (job_list, now)
    return JSONResponse(content=job_list)

async def process_single_job(job):
    try:
        company_names = job.find_all('a', class_='cp_name')
        titles = job.find_all('a', class_='t3_sb')
        img_tags = job.find_all('img')
        salary_tags = job.find_all('span', class_='item b1_sb')
        details_tags = job.find_all('span', class_='item sm')
        location_tags = job.find_all('li', class_='site')
        deadline_tags = job.find_all('td', class_='pd24')

        if not company_names or not titles:
            return {}

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

        return jobs[0]

    except Exception as e:
        print(f"Error processing job: {e}")
        return {}
    
    
    
    
    
    
    