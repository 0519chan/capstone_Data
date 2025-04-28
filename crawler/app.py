#FAST API
import os
from jobkorea_crwaler import crawl_job_data_async
from workent_crawler import crawl_worknet_data
from saramin_crwaler import saramin_job_search
from top10_crwaler import crawl_top100_data_async
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
async def get_workent_jobs(
    keyword: str = Query("데이터 분석", description="검색할 키워드"),
    page: int = Query(1, description="페이지번호"),
    page_size: int = Query(20, description="한 페이지당 결과 수")
    ):
    if 'worknet' in CRAWLER_TYPE:
        jobs = await crawl_worknet_data(keyword, page, page_size)
        return jobs
    return JSONResponse(content={"message": "This service is not for Worknet."}, status_code=400)

@fast_app.get("/top100_api/jobs")
async def get_top100():
    if 'top10' in CRAWLER_TYPE:
        data_list = await crawl_top100_data_async()
        return data_list
    return JSONResponse(content=data_list)

@fast_app.get("/saramin_api/jobs")
async def get_saramin():
    if 'saramin' in CRAWLER_TYPE:
        if not SARAMIN_ACCESS_KEY:
            return JSONResponse(content={"error": "SARAMIN_ACCESS_KEY가 없습니다."}, status_code=500)

        data_list = saramin_job_search(access_key=SARAMIN_ACCESS_KEY)

        saramin_results = data_list.get('jobs', {}).get('job', [])

        if not isinstance(saramin_results, list):
            return JSONResponse(content={"error": "Saramin API 결과가 리스트가 아닙니다."}, status_code=500)

        filtered_results = [extract_saramin_job_info(item) for item in saramin_results]
        return filtered_results

    return JSONResponse(content={"message": "This service is not for Saramin."}, status_code=400)

# @fast_app.on_event("startup")
# async def load_cache_from_file():
#     """서버 시작할 때 파일 캐시 읽어오기"""
#     if os.path.exists(CACHE_FILE):
#         with open(CACHE_FILE, "r", encoding="utf-8") as f:
#             try:
#                 cached_data = json.load(f)
#                 cache['top100'] = (cached_data, time.time())
#                 print("[INFO] Cache loaded from file successfully.")
#             except Exception as e:
#                 print(f"[ERROR] Failed to load cache file: {e}")
#     else:
#         print("[INFO] No cache file found. Will crawl on first request.")


# import os
# import asyncio
# from fastapi import FastAPI, Query
# from fastapi.responses import JSONResponse
# from fastapi.middleware.cors import CORSMiddleware

# from jobkorea_crwaler import crawl_job_data_async as jobkorea_async
# from workent_crawler import crawl_job_data_async as worknet_async
# from top10_crwaler import crawl_top100_data_async

# fast_app = FastAPI()

# fast_app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # 운영 시 필요시 제한
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )
# CRAWLER_TYPE = os.environ.get("CRAWLER_TYPE")
# if not CRAWLER_TYPE:
#     raise ValueError("CRAWLER_TYPE 환경변수가 설정되지 않았습니다.")

# @fast_app.get("/")
# async def home():
#     return JSONResponse(content={"message": "Welcome to the Unified Job Crawler API"})

# @fast_app.get("/jobs")
# async def get_jobs(
#     keyword: str = Query("데이터 분석", description="검색할 키워드")
# ):
#     if CRAWLER_TYPE == "jobkorea":
#         jobs = await jobkorea_async(keyword)
#         return jobs
#     elif CRAWLER_TYPE == "worknet":
#         jobs = await worknet_async(keyword)
#         return jobs
#     elif CRAWLER_TYPE == "top10":
#         jobs = await crawl_top100_data_async()
#         return jobs
#     else:
#         return JSONResponse(content={"message": "Invalid crawler type."}, status_code=400)