import asyncio
import httpx
from bs4 import BeautifulSoup
import urllib.parse
import json
import time

# 특정 검색어에 대한 캐시 (5분 유지)
cache = {}
CACHE_DURATION = 300  # 5 minutes

async def crawl_top100_job_data_async():
    now = time.time()
    keyword = "잡코리아TOP100"

    # 캐시 확인
    if keyword in cache:
        data, timestamp = cache[keyword]
        if now - timestamp < CACHE_DURATION:
            return data

    url = "https://www.jobkorea.co.kr/theme/top100"

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(response.text, "html.parser")
        jobs = soup.select('div.rankList > ul > li')

        tasks = []
        for job in jobs[:100]:  # 100개 하나하기
            tasks.append(process_single_top100_job(client, job))

        job_list = await asyncio.gather(*tasks)

    # 캐시 저장
    cache[keyword] = (job_list, now)
    return job_list

async def process_single_top100_job(client, job):
    try:
        company_name = job.select_one('a.coLink').text.strip()
        title_element = job.select_one('a.tit')

        if title_element:
            job_title = title_element.text.strip()
            detail_link = urllib.parse.urljoin("https://www.jobkorea.co.kr", title_element['href'])
            detail_url = urllib.parse.quote(detail_link, safe=':/&=?')
        else:
            job_title = "제목 없음"
            detail_url = None

        location = job.select_one('span.loc')
        location_text = location.text.strip() if location else "지역 미정"

        salary_text = "협의 가능"
        career_level_text = "경력 무관"
        education_level_text = "학력 무관"
        company_logo_url = "이미지 없음"

        # 세부 페이지 확인
        if detail_url:
            try:
                detail_response = await client.get(detail_url, headers={'User-Agent': 'Mozilla/5.0'})
                detail_soup = BeautifulSoup(detail_response.text, "html.parser")

                # 가금, 경력, 학력 정보 해촌
                info_items = detail_soup.select('div.tbRow.dev-tbRow > span.tbContent')
                if info_items:
                    for item in info_items:
                        text = item.text.strip()
                        if '만원' in text or '회사내규' in text:
                            salary_text = text
                        elif '경력' in text or '신입' in text:
                            career_level_text = text
                        elif '학력' in text or '고졸' in text or '대졸' in text:
                            education_level_text = text

                img_tag = detail_soup.find('img', id='cologo')
                if img_tag and 'src' in img_tag.attrs:
                    company_logo_url = img_tag['src'].strip()

            except Exception as e:
                print(f"Detail page error: {e}")

        return {
            "company_name": company_name,
            "title": job_title,
            "salary": salary_text,
            "career_level": career_level_text,
            "education_level": education_level_text,
            "location": location_text,
            "company_logo_url": company_logo_url,
            "detail_url": detail_url
        }

    except Exception as e:
        print(f"Process job error: {e}")
        return {}

# 실행용 main
async def main():
    jobs = await crawl_top100_job_data_async()
    print(json.dumps(jobs, ensure_ascii=False, indent=4))

if __name__ == "__main__":
    asyncio.run(main())
