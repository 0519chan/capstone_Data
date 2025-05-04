

# import requests
# import json
# headers = {
#         "Authorization": "Basic (base64)",
#         "User-Agent": "Mozilla/5.0 (Docker Client)",
#     }

# def saramin_job_search(access_key, keyword="", start=1, count=20):
#     """
#     사람인 채용공고 API를 호출하는 함수 (개선됨)
#     """
#     try:
#         print(f"도커 환경 내 access_key (호출 직전): {access_key}")  # 추가
#         api_url = f"https://oapi.saramin.co.kr/job-search?access-key={access_key}&keywords={keyword}&start={start}&count={count}&fields=expiration-date"
#         print(f"도커 환경 내 API URL (호출 직전): {api_url}")  # 추가

#         headers = {"Accept": "application/json"}
#         response = requests.get(api_url, headers=headers)

#         response.raise_for_status()

#         return response.json()

#     except requests.exceptions.RequestException as e:
#         print(f"API 호출 중 오류 발생: {e}")
#         if response is not None:
#             print(f"Response Content: {response.text}")
#         return None
#     except ValueError as e:
#         print(f"JSON 파싱 오류: {e}")
#         if response is not None:
#             print(f"Response Content: {response.text}")
#         return None

# def extract_job_info(data):
#     job_list = []

#     for job in data.get("jobs", {}).get("job", []):
#         job_info = {
#             "company": job["company"]["detail"]["name"],
#             "position": job["position"]["title"],
#             "location": job["position"]["location"].get("name", "").replace("&gt;", ">"),
#             "employment_type": job["position"]["job-type"]["name"],
#             "career_level": job["position"]["experience-level"]["name"],
#             "education_level": job["position"]["required-education-level"]["name"],
#             "salary": job["salary"]["name"],
#             "keywords": job["keyword"],
#             "apply_link": job["url"],
#             "company_url": job["company"]["detail"]["href"],
#             "deadline": job.get("expiration-date", "N/A")
#         }
#         job_list.append(job_info)

#     return job_list

# def main():
#     access_key = "iE7rO0FJx5rPtiz6bVrHVGr4KEVBHYCWjSDAm2yWvKIUKB3GkG"
#     keyword = "데이터분석"
#     start = 1
#     count = 20

#     result = saramin_job_search(access_key, keyword, start, count)

#     if result:
#         filtered_jobs = extract_job_info(result)
#         print(json.dumps(filtered_jobs, indent=4, ensure_ascii=False))

# if __name__ == "__main__":
#     main()

import requests
import json
from urllib.parse import quote  # 추가

def crawl_saramin_data(access_key, keyword="", start=1, count=20):
    """
    사람인 채용공고 API를 호출하는 함수 (수정 버전)
    """
    try:
        encoded_keyword = quote(keyword)  # 한글 키워드 인코딩

        print(f"도커 환경 내 access_key (호출 직전): {access_key}")  
        api_url = f"https://oapi.saramin.co.kr/job-search?access-key={access_key}&keywords={encoded_keyword}&start={start}&count={count}&fields=expiration-date"
        print(f"도커 환경 내 API URL (호출 직전): {api_url}")  

        headers = {
            "User-Agent": "Mozilla/5.0 (Docker Client)",
            "Accept": "application/json",
            "Referer": "https://oapi.saramin.co.kr",  # 추가
        }

        response = requests.get(api_url, headers=headers)
        response.raise_for_status()

        return response.json()

    except requests.exceptions.RequestException as e:
        print(f"API 호출 중 오류 발생: {e}")
        if response is not None:
            print(f"Response Content: {response.text}")
        return None
    except ValueError as e:
        print(f"JSON 파싱 오류: {e}")
        if response is not None:
            print(f"Response Content: {response.text}")
        return None

def extract_job_info(data):
    job_list = []

    for job in data.get("jobs", {}).get("job", []):
        job_info = {
            "company": job["company"]["detail"]["name"],
            "position": job["position"]["title"],
            "location": job["position"]["location"].get("name", "").replace("&gt;", ">"),
            "employment_type": job["position"]["job-type"]["name"],
            "career_level": job["position"]["experience-level"]["name"],
            "education_level": job["position"]["required-education-level"]["name"],
            "salary": job["salary"]["name"],
            "keywords": job["keyword"],
            "apply_link": job["url"],
            "company_url": job["company"]["detail"]["href"],
            "deadline": job.get("expiration-date", "N/A")
        }
        job_list.append(job_info)

    return job_list

def main():
    #access_key = "iE7rO0FJx5rPtiz6bVrHVGr4KEVBHYCWjSDAm2yWvKIUKB3GkG"
    keyword = "데이터분석"
    start = 1
    count = 20

    result = crawl_saramin_data( keyword, start, count)

    if result:
        filtered_jobs = extract_job_info(result)
        print(json.dumps(filtered_jobs, indent=4, ensure_ascii=False))

if __name__ == "__main__":
    main()