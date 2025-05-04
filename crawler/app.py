# #FAST API
# import os
# from jobkorea_crwaler import crawl_job_data_async
# from workent_crawler import crawl_worknet_data
# from saramin_crwaler import crawl_saramin_data
# from top10_crwaler import crawl_top100_data_async
# from fastapi import FastAPI, Query
# from fastapi.responses import JSONResponse
# from fastapi.middleware.cors import CORSMiddleware

# fast_app = FastAPI()

# origins = [
#     "http://localhost:3000",
#     # 필요한 다른 origin들을 추가하세요
# ]

# fast_app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )


# SARAMIN_ACCESS_KEY = os.environ.get("SARAMIN_ACCESS_KEY")
# CRAWLER_TYPE = os.environ.get("CRAWLER_TYPE")
# def extract_saramin_job_info(item: dict) -> dict:
#         return {
#             "title": item.get("position", {}).get("title", "제목 없음"),
#             "company_name": item.get("company", {}).get("detail", {}).get("name", "회사명 없음"),
#             "location": item.get("position", {}).get("location", {}).get("name", "지역 없음").replace("&gt;", ">"),
#             "education_level": item.get("position", {}).get("required-education-level", {}).get("name", "학력 정보 없음"),
#             "career_level": item.get("position", {}).get("experience-level", {}).get("name", "경력 정보 없음"),
#             "salary": item.get("salary", {}).get("name", "급여 정보 없음"),
#             "expiration_date": item.get("expiration-date", "마감일 정보 없음"),
#             "detail_url": item.get("url", "링크 없음")
#         }


# @fast_app.get("/")
# async def home():
#     return JSONResponse(content={"message": "Welcome to the Jobkorea Crawler API"})

# CRAWLER_TYPE =  ['jobkorea', 'worknet', 'total_cralwer', 'saramin']  # 실제 운영 값에 맞게 설정

# @fast_app.get("/jobkorea_api/jobs")
# async def get_jobkorea_jobs(
#     keyword: str = Query("스포츠", description="검색 키워드"),
#     page: int = Query(4, description="페이지 번호"),
#     page_size: int = Query(20, description="한 페이지당 결과 수")
# ):
#     if 'jobkorea' in CRAWLER_TYPE:
#         jobs = await crawl_job_data_async(keyword, page, page_size)  # 수정!!
#         return jobs

#     return JSONResponse(content={"message": "This service is not for Jobkorea."}, status_code=400)



# @fast_app.get("/worknet_api/jobs")
# async def get_workent_jobs(
#     keyword: str = Query("데이터 분석", description="검색할 키워드"),
#     page: int = Query(1, description="페이지번호"),
#     page_size: int = Query(20, description="한 페이지당 결과 수")
#     ):
#     if 'worknet' in CRAWLER_TYPE:
#         jobs = await crawl_worknet_data(keyword, page, page_size)
#         return jobs
#     return JSONResponse(content={"message": "This service is not for Worknet."}, status_code=400)

# @fast_app.get("/top100_api/jobs")
# async def get_top100():
#     if 'top10' in CRAWLER_TYPE:
#         data_list = await crawl_top100_data_async()
#         return data_list
#     return JSONResponse(content=data_list)

# @fast_app.get("/saramin_api/jobs")
# async def get_saramin():
#     if 'saramin' in CRAWLER_TYPE:
#         if not SARAMIN_ACCESS_KEY:
#             return JSONResponse(content={"error": "SARAMIN_ACCESS_KEY가 없습니다."}, status_code=500)

#         data_list = crawl_saramin_data(access_key=SARAMIN_ACCESS_KEY)

#         saramin_results = data_list.get('jobs', {}).get('job', [])

#         if not isinstance(saramin_results, list):
#             return JSONResponse(content={"error": "Saramin API 결과가 리스트가 아닙니다."}, status_code=500)

#         filtered_results = [extract_saramin_job_info(item) for item in saramin_results]
#         return filtered_results

#     return JSONResponse(content={"message": "This service is not for Saramin."}, status_code=400)


#FAST API
import os
from jobkorea_crwaler import crawl_job_data_async
from workent_crawler import crawl_worknet_data
from saramin_crwaler import crawl_saramin_data
from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

fast_app = FastAPI()

origins = [
    "http://localhost:3000",
    # 필요한 다른 origin들을 추가하세요
]

fast_app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


SARAMIN_ACCESS_KEY = os.environ.get("SARAMIN_ACCESS_KEY")
CRAWLER_TYPE = os.environ.get("CRAWLER_TYPE")
def extract_saramin_job_info(item: dict) -> dict:
        return {
            "title": item.get("position", {}).get("title", "제목 없음"),
            "company_name": item.get("company", {}).get("detail", {}).get("name", "회사명 없음"),
            "location": item.get("position", {}).get("location", {}).get("name", "지역 없음").replace("&gt;", ">"),
            "education_level": item.get("position", {}).get("required-education-level", {}).get("name", "학력 정보 없음"),
            "career_level": item.get("position", {}).get("experience-level", {}).get("name", "경력 정보 없음"),
            "salary": item.get("salary", {}).get("name", "급여 정보 없음"),
            "expiration_date": item.get("expiration-date", "마감일 정보 없음"),
            "detail_url": item.get("url", "링크 없음")
        }


@fast_app.get("/")
async def home():
    return JSONResponse(content={"message": "Welcome to the Jobkorea Crawler API"})

CRAWLER_TYPE =  ['jobkorea', 'worknet', 'top10', 'saramin']  # 실제 운영 값에 맞게 설정

@fast_app.get("/jobkorea_api/jobs")
async def get_jobkorea_jobs(
    keyword: str = Query("스포츠", description="검색 키워드"),
    page: int = Query(4, description="페이지 번호"),
    page_size: int = Query(20, description="한 페이지당 결과 수")
):
    if 'jobkorea' in CRAWLER_TYPE:
        jobs = await crawl_job_data_async(keyword, page, page_size)  # 수정!!
        return jobs

    return JSONResponse(content={"message": "This service is not for Jobkorea."}, status_code=400)



@fast_app.get("/worknet_api/jobs")
async def worknet_endpoint(keyword: str = Query('데이터분석'), page: int = Query(1), page_size: int = Query(5)):
    if 'worknet' in CRAWLER_TYPE:
        jobs = await crawl_worknet_data(keyword, page, page_size)
        return jobs
    return JSONResponse(content={"message": "This service is not for Worknet."}, status_code=400)


@fast_app.get("/saramin_api/jobs")
async def get_saramin():
    if 'saramin' in CRAWLER_TYPE:
        if not SARAMIN_ACCESS_KEY:
            return JSONResponse(content={"error": "SARAMIN_ACCESS_KEY가 없습니다."}, status_code=500)

        data_list = crawl_saramin_data(access_key=SARAMIN_ACCESS_KEY)

        saramin_results = data_list.get('jobs', {}).get('job', [])

        if not isinstance(saramin_results, list):
            return JSONResponse(content={"error": "Saramin API 결과가 리스트가 아닙니다."}, status_code=500)

        filtered_results = [extract_saramin_job_info(item) for item in saramin_results]
        return filtered_results

    return JSONResponse(content={"message": "This service is not for Saramin."}, status_code=400)

@fast_app.get("/integrated_api/jobs")
async def get_integrated_jobs(
    keyword: str = Query("데이터 분석", description="검색할 키워드"),
    page: int = Query(1, description="페이지 번호"),
    page_size: int = Query(10, description="한 번에 가져올 개수")
):
    results = []

    # Jobkorea 크롤링
    if 'jobkorea' in CRAWLER_TYPE:
        try:
            jobkorea_jobs = await crawl_job_data_async(keyword, page, page_size)
            if isinstance(jobkorea_jobs, list):
                for job in jobkorea_jobs:
                    job["source"] = "jobkorea"
                results.extend(jobkorea_jobs)
            else:
                print("[JobKorea 경고] 반환값이 리스트가 아닙니다.")
        except Exception as e:
            print(f"[JobKorea 오류] {e}")

    # Worknet 크롤링
    if 'worknet' in CRAWLER_TYPE:
        try:
            worknet_jobs = await worknet_endpoint(keyword, page, page_size)
            if isinstance(worknet_jobs, list):
                for job in worknet_jobs:
                    job["source"] = "worknet"
                results.extend(worknet_jobs)
            else:
                print("[Worknet 경고] 반환값이 리스트가 아닙니다.")
        except Exception as e:
            print(f"[Worknet 오류] {e}")

    # Saramin 크롤링
    if 'saramin' in CRAWLER_TYPE and SARAMIN_ACCESS_KEY:
        try:
            data_list = crawl_saramin_data(access_key=SARAMIN_ACCESS_KEY)
            saramin_jobs = data_list.get('jobs', {}).get('job', [])
            if isinstance(saramin_jobs, list):
                filtered = [extract_saramin_job_info(item) for item in saramin_jobs[:page_size]]
                for job in filtered:
                    job["source"] = "saramin"
                results.extend(filtered)
            else:
                print("[Saramin 경고] 반환값이 리스트가 아닙니다.")
        except Exception as e:
            print(f"[Saramin 오류] {e}")

    return results
