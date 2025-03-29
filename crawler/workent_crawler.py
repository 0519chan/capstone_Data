# import requests
# from bs4 import BeautifulSoup
# import urllib.parse

# def crawl_job_data(keyword):
#     encoded_keyword = urllib.parse.quote(keyword)
#     url = f"https://www.work24.go.kr/wk/a/b/1200/retriveDtlEmpSrchList.do?startCount=1&topQuerySearchArea=all&searchYn=Y&listCount=5&keyword=&srcKeyword={encoded_keyword}&programMenuIdentification=EBG020000000000"

#     headers = {'User-Agent': 'Mozilla/5.0'}
#     response = requests.get(url, headers=headers)

#     if response.status_code == 200:
#         soup = BeautifulSoup(response.text, "html.parser")
#         main = soup.select('div.box_table_wrap')

#         print("채용 정보 목록")

#         job_number = 1  # 순차 번호를 위한 카운터 초기화

#         for info in main:
#             company_names = info.find_all('a', class_='cp_name')
#             titles = info.find_all('a', class_='t3_sb')
#             img_tags = info.find_all('img')
#             salary_tags = info.find_all('span', class_='item b1_sb')
#             details_tags = info.find_all('span', class_='item sm')  # 경력 및 학력 정보
#             location_tags = info.find_all('li', class_='site')  # 지역 정보 크롤링

#             if not company_names:
#                 continue  # Skip if no job postings in this section

#             for idx, (company, title) in enumerate(zip(company_names, titles)):
#                 print(f"\n[{job_number}] 회사명: {company.text.strip()}")
#                 print(f"채용 제목: {title.text.strip()}")

#                 # 연봉 정보 추출
#                 salary = salary_tags[idx].get_text(strip=True).replace("\n", "").replace("\t", "") if idx < len(salary_tags) else "정보 없음"
#                 salary_range = salary.split('~') if '~' in salary else ["정보 없음", "정보 없음"]
#                 print(f"연봉: 최소 {salary_range[0].strip()}만원 ~ 최대 {salary_range[1].strip()}만원")

#                 # 경력 및 학력 정보 추출
#                 experience = details_tags[idx * 2].get_text(strip=True) if idx * 2 < len(details_tags) else "정보 없음"
#                 education = details_tags[idx * 2 + 1].get_text(strip=True) if idx * 2 + 1 < len(details_tags) else "정보 없음"
#                 print(f"경력: {experience}")
#                 print(f"학력: {education}")

#                 # 지역 정보 추출
#                 location = location_tags[idx].get_text(strip=True) if idx < len(location_tags) else "정보 없음"
#                 print(f"지역: {location}")

#                 # 이미지 경로 보정
#                 img_tag = img_tags[idx] if idx < len(img_tags) else None
#                 img_src = img_tag['src'].strip() if img_tag and 'src' in img_tag.attrs else "이미지 없음"
#                 if not img_src.startswith("http"):
#                     img_src = "https://www.work24.go.kr" + img_src
#                 print(f"로고 이미지: {img_src}")

#                 # 상세 페이지 URL 추출 및 접근
#                 link_tag = titles[idx]
#                 link = link_tag.get('href')
#                 full_link = urllib.parse.urljoin("https://work24.go.kr", link)  # 상대 경로를 절대 경로로 변환
#                 print(f"상세 페이지 URL: {full_link}")  # 확인용 출력

#                 if full_link:
#                     response_detail = requests.get(full_link, headers={'User-Agent': 'Mozilla/5.0'})

#                     if response_detail.status_code == 200:
#                         soup_detail = BeautifulSoup(response_detail.text, "html.parser")
#                         company_info_tags = soup_detail.find('div', 'flex_box flex_al_s gap40 flex1')

#                         if company_info_tags:
#                             # 기업 정보 저장 딕셔너리
#                             company_info = {}

#                             # 모든 li 태그 가져오기
#                             info_items = company_info_tags.find_all('li')

#                             for item in info_items:
#                                 title_tag = item.find('em', class_='tit')  # <em class="tit">태그 찾기
#                                 if title_tag:
#                                     key = title_tag.text.strip()  # 항목명

#                                     # next_sibling이 없거나 공백이 많을 경우 get_text() 활용
#                                     value = title_tag.next_sibling
#                                     if value:
#                                         value = value.strip()
#                                     else:
#                                         # 전체 텍스트를 가져와서 key 값(항목명)을 제외한 텍스트 추출
#                                         value = item.get_text(separator=" ", strip=True).replace(key, "").strip()

#                                     # 연속된 공백 제거
#                                     value = " ".join(value.split())

#                                     company_info[key] = value  # 딕셔너리에 저장

#                             # 기업 정보 출력 (각 채용 정보별로 출력)
#                             print(f"\n  기업 정보:")
#                             for key, value in company_info.items():
#                                 print(f"  {key}: {value}")
#                         else:
#                             print("  기업 정보 없음")

#                     else:
#                         print(f"  상세 페이지 요청 실패: {response_detail.status_code}")

#                 job_number += 1  # 다음 채용 정보를 위해 카운터 증가

#     else:
#         print(f"요청 실패: 상태 코드 {response.status_code}")

# crawl_job_data('데이터 분석')


import requests
from bs4 import BeautifulSoup
import urllib.parse
import json

def crawl_job_data(keyword):
    encoded_keyword = urllib.parse.quote(keyword)
    url = f"https://www.work24.go.kr/wk/a/b/1200/retriveDtlEmpSrchList.do?startCount=1&topQuerySearchArea=all&searchYn=Y&listCount=5&keyword=&srcKeyword={encoded_keyword}&programMenuIdentification=EBG020000000000"

    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)

    job_list = []

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        main = soup.select('div.box_table_wrap')

        job_number = 1

        for info in main:
            company_names = info.find_all('a', class_='cp_name')
            titles = info.find_all('a', class_='t3_sb')
            img_tags = info.find_all('img')
            salary_tags = info.find_all('span', class_='item b1_sb')
            details_tags = info.find_all('span', class_='item sm')
            location_tags = info.find_all('li', class_='site')

            if not company_names:
                continue

            for idx, (company, title) in enumerate(zip(company_names, titles)):
                job_data = {
                    "company_name": company.text.strip(),
                    "title": title.text.strip(),
                    "salary": "정보 없음",
                    "career_level": "정보 없음",
                    "education_level": "정보 없음",
                    "location": "정보 없음",
                    "company_logo_url": "이미지 없음",
                    "details_url": ""
                }

                salary = salary_tags[idx].get_text(strip=True).replace("\n", "").replace("\t", "").replace("\r", "") if idx < len(salary_tags) else "정보 없음"
                job_data["salary"] = salary.strip()

                if idx * 2 < len(details_tags):
                    job_data["experience"] = details_tags[idx * 2].get_text(strip=True)
                if idx * 2 + 1 < len(details_tags):
                    job_data["education"] = details_tags[idx * 2 + 1].get_text(strip=True)

                if idx < len(location_tags):
                    job_data["location"] = location_tags[idx].get_text(strip=True)

                img_tag = img_tags[idx] if idx < len(img_tags) else None
                img_src = img_tag['src'].strip() if img_tag and 'src' in img_tag.attrs else "이미지 없음"
                if not img_src.startswith("http"):
                    img_src = "https://www.work24.go.kr" + img_src
                job_data["company_log_url"] = img_src

                link_tag = titles[idx]
                link = link_tag.get('href')
                full_link = urllib.parse.urljoin("https://work24.go.kr", link)
                job_data["details_url"] = full_link

                job_list.append(job_data)
                job_number += 1

    else:
        return json.dumps({"error": f"요청 실패: 상태 코드 {response.status_code}"}, ensure_ascii=False, indent=4)

    return json.dumps(job_list, ensure_ascii=False, indent=4)

# 실행 예제
print(crawl_job_data('데이터 분석'))

