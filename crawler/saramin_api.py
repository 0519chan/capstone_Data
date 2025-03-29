import requests
import urllib.parse
import json

def saramin_job_search(access_key, keyword="", start=1, count=20):
    """
    사람인 채용공고 API를 호출하는 함수 (개선됨)
    """
    try:
        #encoded_keyword = urllib.parse.quote(keyword)
        api_url = f"https://oapi.saramin.co.kr/job-search?access-key={access_key}&keywords={keyword}&start={start}&count={count}"
        print(api_url)

        headers = {"Accept": "application/json"}
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

def main():
    access_key = "iE7rO0FJx5rPtiz6bVrHVGr4KEVBHYCWjSDAm2yWvKIUKB3GkG"
    keyword = "데이터분석"
    start = 1
    count = 20

    result = saramin_job_search(access_key, keyword, start, count)

    if result:
        print(json.dumps(result, indent=4, ensure_ascii=False))

if __name__ == "__main__":
    main()

