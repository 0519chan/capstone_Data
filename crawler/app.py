import os
import asyncio
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from jobkorea_crwaler import crawl_job_data_async
from workent_crawler import crawl_job_data as worknet_crawler
from saramin_crwaler import saramin_job_search, extract_job_info
from top10 import crawl_top100_job_data_async 

SARAMIN_ACCESS_KEY = os.environ.get("SARAMIN_ACCESS_KEY")
CRAWLER_TYPE = os.environ.get("CRAWLER_TYPE")

app = Flask(__name__)
CORS(app, origins="http://localhost:3000")

# 메인 페이지 (프론트엔드 연결)
@app.route('/')
def home():
    return render_template("index.html")

# 잡코리아 API
@app.route('/jobkorea_api/jobs', methods=['GET'])
def get_jobkorea_jobs():
    if CRAWLER_TYPE == 'jobkorea':
        keyword = request.args.get('keyword', '데이터 분석')
        jobs = asyncio.run(crawl_job_data_async(keyword))
        return jsonify(jobs)
    return jsonify({"message": "This service is not for Jobkorea."}), 400

# 워크넷 API
@app.route('/worknet_api/jobs', methods=['GET'])
def get_worknet_jobs():
    if CRAWLER_TYPE == 'worknet':
        keyword = request.args.get('keyword', '데이터 분석')
        jobs = worknet_crawler(keyword)
        return jsonify(jobs)
    return jsonify({"message": "This service is not for Worknet."}), 400

# 사람인 API
@app.route('/saramin_api/jobs', methods=['GET'])
def get_saramin_jobs():
    if CRAWLER_TYPE == 'saramin':
        if not SARAMIN_ACCESS_KEY:
            return jsonify({"error": "SARAMIN_ACCESS_KEY가 설정되지 않았습니다."}), 500
        keyword = request.args.get('keyword', '데이터 분석')
        start = request.args.get('start', 1, type=int)
        count = request.args.get('count', 20, type=int)

        result = saramin_job_search(SARAMIN_ACCESS_KEY, keyword, start, count)

        if result:
            filtered_jobs = extract_job_info(result)
            return jsonify(filtered_jobs)
        else:
            return jsonify({"error": "사람인 API 호출 실패"}), 500
    return jsonify({"message": "This service is not for Saramin."}), 400


@app.route('/top10_api/jobs', methods=['GET'])
def get_top10_crawler():
    if CRAWLER_TYPE == 'top10':
        top10 = asyncio.run(crawl_job_data_async())
        return jsonify(top10)
    return jsonify({"message": "This service is not for top10."}), 400



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)



# import os
# import threading
# from flask import Flask, jsonify, request, render_template
# from flask_cors import CORS
# from jobkorea_crwaler import crawl_job_data as jobkorea_crawler
# from workent_crawler import crawl_job_data as worknet_crawler
# from saramin_crwaler import saramin_job_search, extract_job_info

# SARAMIN_ACCESS_KEY = os.environ.get("SARAMIN_ACCESS_KEY")
# CRAWLER_TYPE = os.environ.get("CRAWLER_TYPE")

# app = Flask(__name__)
# CORS(app, origins="http://localhost:4040")

# # 메인 페이지
# @app.route('/')
# def home():
#     return render_template("index.html")

# # 크롤링 API
# @app.route('/crawl-now', methods=['GET'])
# def crawl_now():
#     keyword = request.args.get('keyword', '데이터 분석')
#     if CRAWLER_TYPE == 'jobkorea':
#         jobs = jobkorea_crawler(keyword)
#     elif CRAWLER_TYPE == 'worknet':
#         jobs = worknet_crawler(keyword)
#     elif CRAWLER_TYPE == 'saramin':
#         if not SARAMIN_ACCESS_KEY:
#             return jsonify({"error": "SARAMIN_ACCESS_KEY가 설정되지 않았습니다."}), 500
#         result = saramin_job_search(SARAMIN_ACCESS_KEY, keyword)
#         jobs = extract_job_info(result)
#     else:
#         return jsonify({"error": "지원하지 않는 크롤러 타입입니다."}), 400

#     return jsonify(jobs)

# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=5000)