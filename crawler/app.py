from flask import Flask, jsonify, request
from flask_cors import CORS
from jobkorea_crwaler import crawl_job_data
from workent_crawler import crawl_job_data

app = Flask(__name__)
CORS(app, origins="http://localhost:3000")  # 웹 페이지의 출처를 명시적으로 허용

@app.route('/')  # 루트 경로 추가
def home():
    return "Hello! This is the Crawler API Server."

@app.route('/jobkorea_api/jobs', methods=['GET'])
def get_jobkrea_jobs():
    keyword = request.args.get('keyword', '데이터 분석')
    jobs = crawl_job_data(keyword)
    return jsonify(jobs)

@app.route('/worknet_api/jobs', methods=['GET'])
def get_worknet_jobs():
    keyword = request.args.get('keyword', '데이터 분석')
    jobs = crawl_job_data(keyword)
    return jsonify(jobs)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)