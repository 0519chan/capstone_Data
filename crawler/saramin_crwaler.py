import requests
import json
from urllib.parse import quote, urlparse, parse_qs


def crawl_saramin_data(access_key, keyword="", start=1, count=20):
    """
    사람인 채용공고 API를 호출하여 데이터 반환
    """
    try:
        # keyword가 None이면 빈 문자열로 처리
        encoded_keyword = quote(str(keyword or ""))

        api_url = (
            f"https://oapi.saramin.co.kr/job-search"
            f"?access-key={access_key}"
            f"&keywords={encoded_keyword}"
            f"&start={start}&count={count}"
            f"&fields=expiration-date"
        )

        headers = {
            "User-Agent": "Mozilla/5.0 (Docker Client)",
            "Accept": "application/json",
            "Referer": "https://oapi.saramin.co.kr",
        }

        response = requests.get(api_url, headers=headers)
        response.raise_for_status()
        return response.json()

    except requests.exceptions.RequestException as e:
        print(f"[사람인 오류] 요청 실패: {e}")
        return None
    except ValueError as e:
        print(f"[사람인 오류] JSON 파싱 실패: {e}")
        return None


def extract_job_info(data):
    """
    사람인 API 응답에서 필요한 항목 추출
    """
    job_list = []
    for job in data.get("jobs", {}).get("job", []):
        job_info = {
            "company": job.get("company", {}).get("detail", {}).get("name", "정보 없음"),
            "position": job.get("position", {}).get("title", "정보 없음"),
            "location": job.get("position", {}).get("location", {}).get("name", "").replace("&gt;", ">"),
            "employment_type": job.get("position", {}).get("job-type", {}).get("name", "정보 없음"),
            "career_level": job.get("position", {}).get("experience-level", {}).get("name", "정보 없음"),
            "education_level": job.get("position", {}).get("required-education-level", {}).get("name", "정보 없음"),
            "salary": job.get("salary", {}).get("name", "정보 없음"),
            "keywords": job.get("keyword", []),
            "apply_link": job.get("url", "링크 없음"),
            "company_url": job.get("company", {}).get("detail", {}).get("href", "링크 없음"),
            "deadline": job.get("expiration-date", "마감일 없음"),
        }
        job_list.append(job_info)
    return job_list


def crawl_saramin_detail(url: str) -> dict:
    """
    공고 상세 페이지 URL로 iframe 링크 생성
    """
    try:
        parsed = urlparse(url)
        query_params = parse_qs(parsed.query)
        rec_idx = query_params.get("rec_idx", [None])[0]

        if not rec_idx:
            return {"type": "error", "content": "rec_idx 파라미터가 누락되었습니다."}

        iframe_url = f"https://www.saramin.co.kr/api/jobs/job/content?rec_idx={rec_idx}"
        return {
            "type": "iframe",
            "content": iframe_url
        }

    except Exception as e:
        return {
            "type": "error",
            "content": str(e)
        }


# ✅ 개발용 테스트용 함수 (운영에는 필요 없음)
def main():
    import os
    access_key = os.getenv("SARAMIN_ACCESS_KEY", "")
    keyword = "데이터분석"

    result = crawl_saramin_data(access_key, keyword, start=1, count=5)
    if result:
        jobs = extract_job_info(result)
        print(json.dumps(jobs, indent=4, ensure_ascii=False))


if __name__ == "__main__":
    main()