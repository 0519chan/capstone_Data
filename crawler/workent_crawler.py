# import requests
# from bs4 import BeautifulSoup
# import urllib.parse
# import json

# def crawl_job_data(keyword):
#     encoded_keyword = urllib.parse.quote(keyword)
#     url = f"https://www.work24.go.kr/wk/a/b/1200/retriveDtlEmpSrchList.do?startCount=1&topQuerySearchArea=all&searchYn=Y&listCount=5&keyword=&srcKeyword={encoded_keyword}&programMenuIdentification=EBG020000000000"

#     headers = {'User-Agent': 'Mozilla/5.0'}
#     response = requests.get(url, headers=headers)

#     job_list = []

#     if response.status_code == 200:
#         soup = BeautifulSoup(response.text, "html.parser")
#         main = soup.select('div.box_table_wrap')

#         job_number = 1

#         for info in main:
#             company_names = info.find_all('a', class_='cp_name')
#             titles = info.find_all('a', class_='t3_sb')
#             img_tags = info.find_all('img')
#             salary_tags = info.find_all('span', class_='item b1_sb')
#             details_tags = info.find_all('span', class_='item sm')
#             location_tags = info.find_all('li', class_='site')

#             if not company_names:
#                 continue

#             for idx, (company, title) in enumerate(zip(company_names, titles)):
#                 job_data = {
#                     "company_name": company.text.strip(),
#                     "title": title.text.strip(),
#                     "salary": "정보 없음",
#                     "career_level": "정보 없음",
#                     "education_level": "정보 없음",
#                     "location": "정보 없음",
#                     "company_logo_url": "이미지 없음",
#                     "details_url": ""
#                 }

#                 salary = salary_tags[idx].get_text(strip=True).replace("\n", "").replace("\t", "").replace("\r", "") if idx < len(salary_tags) else "정보 없음"
#                 job_data["salary"] = salary.strip()

#                 if idx * 2 < len(details_tags):
#                     job_data["experience"] = details_tags[idx * 2].get_text(strip=True)
#                 if idx * 2 + 1 < len(details_tags):
#                     job_data["education"] = details_tags[idx * 2 + 1].get_text(strip=True)

#                 if idx < len(location_tags):
#                     job_data["location"] = location_tags[idx].get_text(strip=True)

#                 img_tag = img_tags[idx] if idx < len(img_tags) else None
#                 img_src = img_tag['src'].strip() if img_tag and 'src' in img_tag.attrs else "이미지 없음"
#                 if not img_src.startswith("http"):
#                     img_src = "https://www.work24.go.kr" + img_src
#                 job_data["company_log_url"] = img_src

#                 link_tag = titles[idx]
#                 link = link_tag.get('href')
#                 full_link = urllib.parse.urljoin("https://work24.go.kr", link)
#                 job_data["details_url"] = full_link

#                 job_list.append(job_data)
#                 job_number += 1

#     else:
#         return json.dumps({"error": f"요청 실패: 상태 코드 {response.status_code}"}, ensure_ascii=False, indent=4)

#     return json.dumps(job_list, ensure_ascii=False, indent=4)

# # 실행 예제
# print(crawl_job_data('데이터 분석'))


import requests
from bs4 import BeautifulSoup
import urllib.parse
import json
import re

def crawl_job_data(keyword):
    encoded_keyword = urllib.parse.quote(keyword)
    url = f"https://www.work24.go.kr/wk/a/b/1200/retriveDtlEmpSrchList.do?startCount=1&topQuerySearchArea=all&searchYn=Y&listCount=5&keyword=&srcKeyword={encoded_keyword}&programMenuIdentification=EBG020000000000"

    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)

    job_list = []

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        main = soup.select('div.box_table_wrap')

        temp_list = []

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
                # salary 정제 처리
                raw_salary = salary_tags[idx].get_text(strip=True) if idx < len(salary_tags) else "정보 없음"
                clean_salary = re.sub(r'[\r\n\t\s]', '', raw_salary)  # 특수문자 제거

                # 숫자가 있으면 포맷 변경
                salary_match = re.search(r'(\d[\d,]*)', clean_salary)
                if salary_match:
                    clean_salary = f"연봉 {salary_match.group(1)}원"

                job_data = {
                    "company_name": company.text.strip() if company else "정보 없음",
                    "title": title.text.strip() if title else "정보 없음",
                    "salary": clean_salary if clean_salary else "정보 없음",
                    "experience": details_tags[idx * 2].get_text(strip=True) if idx * 2 < len(details_tags) else "정보 없음",
                    "education": details_tags[idx * 2 + 1].get_text(strip=True) if idx * 2 + 1 < len(details_tags) else "정보 없음",
                    "location": location_tags[idx].get_text(strip=True) if idx < len(location_tags) else "정보 없음",
                    "company_logo_url": "이미지 없음",
                    "details_url": ""
                }

                img_tag = img_tags[idx] if idx < len(img_tags) else None
                img_src = img_tag['src'].strip() if img_tag and 'src' in img_tag.attrs else "이미지 없음"
                if img_src != "이미지 없음" and not img_src.startswith("http"):
                    img_src = "https://www.work24.go.kr" + img_src
                job_data["company_logo_url"] = img_src

                link_tag = title
                link = link_tag.get('href') if link_tag else ""
                full_link = urllib.parse.urljoin("https://work24.go.kr", link) if link else "정보 없음"
                job_data["details_url"] = full_link

                temp_list.append(job_data)

        # 2차 파싱: 중복 제거
        seen = set()
        for item in temp_list:
            identifier = (item['company_name'], item['title'])
            if identifier not in seen:
                seen.add(identifier)
                job_list.append(item)

    else:
        return json.dumps({"error": f"요청 실패: 상태 코드 {response.status_code}"}, ensure_ascii=False, indent=4)

    return json.dumps(job_list, ensure_ascii=False, indent=4)

# 실행 예제
#print(crawl_job_data('데이터 분석'))