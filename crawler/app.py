
from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from jobkorea_crwaler import crawl_job_data_async, crawl_job_detail_async
from saramin_crwaler import crawl_saramin_data, crawl_saramin_detail
from workent_crawler import crawl_worknet_data, crawl_worknet_detail
import os
import sys


fast_app = FastAPI()
SARAMIN_ACCESS_KEY = os.environ.get("SARAMIN_ACCESS_KEY")

origins = ["http://localhost:3000"]
fast_app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@fast_app.get("/api/jobs")
async def get_jobs(
    source: str = Query(..., enum=["jobkorea", "saramin", "worknet"]),
    keyword: str = Query('데이터분석'),
    page: int = Query(1),
    page_size: int = Query(10)
):
    if source == "jobkorea":
        return await crawl_job_data_async(keyword, page, page_size)
    elif source == "saramin":
        saramin_access_key = os.getenv("SARAMIN_ACCESS_KEY")
        if not saramin_access_key:
            print("ERROR: SARAMIN_ACCESS_KEY is not set in environment.", file=sys.stderr)
            return JSONResponse(content={"error": "SARAMIN_ACCESS_KEY 환경 변수가 설정되지 않았습니다."}, status_code=500)
        return crawl_saramin_data(saramin_access_key, keyword, page, page_size)
    elif source == "worknet":
        return await crawl_worknet_data(keyword, page, page_size)
    else:
        return JSONResponse(content={"error": "지원하지 않는 소스입니다."}, status_code=400)
    
    
@fast_app.get("/api/detail")
async def get_detail(
    source: str = Query(..., enum=["jobkorea", "saramin", "worknet"]),
    url: str = Query(...)
):
    if source == "jobkorea":
        return await crawl_job_detail_async(url)
    elif source == "saramin":
        return crawl_saramin_detail(url)
    elif source == "worknet":
         return await crawl_worknet_detail(url)
    else:
        return JSONResponse(content={"error": "지원하지 않는 소스입니다."}, status_code=400)

@fast_app.get("/integrated_api/jobs")
async def get_integrated_jobs(
    keyword: str = Query("데이터 분석", description="검색할 키워드"),
    page: int = Query(1, description="페이지 번호"),
    page_size: int = Query(10, description="한 번에 가져올 개수")
):
    results = []

    # Jobkorea 크롤링
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
    try:
        worknet_jobs = await crawl_worknet_data(keyword, page, page_size)
        if isinstance(worknet_jobs, list):
            for job in worknet_jobs:
                job["source"] = "worknet"
            results.extend(worknet_jobs)
        else:
            print("[Worknet 경고] 반환값이 리스트가 아닙니다.")
    except Exception as e:
        print(f"[Worknet 오류] {e}")

    # Saramin 크롤링
    try:
        saramin_access_key = os.getenv("SARAMIN_ACCESS_KEY")

      
        if not saramin_access_key:
            print("ERROR: SARAMIN_ACCESS_KEY is not set or empty for Saramin.", file=sys.stderr)
            raise ValueError("SARAMIN_ACCESS_KEY 환경 변수가 설정되지 않았습니다.") 
        saramin_data = crawl_saramin_data(access_key=saramin_access_key, keyword=keyword, start=page, count=page_size) # start와 count는 page와 page_size로 매핑

        saramin_jobs = saramin_data.get('jobs', {}).get('job', [])
        if isinstance(saramin_jobs, list):       
            for job in saramin_jobs[:page_size]: 
                job["source"] = "saramin"
                results.append(job)
        else:
            print(f"[Saramin 경고] 반환값이 리스트가 아닙니다. 응답: {saramin_data}", file=sys.stderr)
            pass 
    except Exception as e:
        print(f"[Saramin 오류] API 호출 중 예외 발생: {e}", file=sys.stderr)

        pass

    return results



@fast_app.get("/integrated_api/detail")
async def get_integrated_detail(
    source: str = Query(..., enum=["jobkorea", "saramin", "worknet"]),
    url: str = Query(...)
):
    try:
        if source == "jobkorea":
            return await crawl_job_detail_async(url)
        elif source == "saramin":
            return crawl_saramin_detail(url)
        elif source == "worknet":
            return await crawl_worknet_detail(url)
        else:
            return JSONResponse(content={"error": "지원하지 않는 소스입니다."}, status_code=400)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


