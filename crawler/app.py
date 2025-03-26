from flask import Flask, jsonify, request
from crawler import crawl_job_data

app = Flask(__name__)

@app.route('/')  # 루트 경로 추가
def home():
    return "Hello! This is the Crawler API Server."

@app.route('/api/jobs', methods=['GET'])
def get_jobs():
    keyword = request.args.get('keyword', '데이터 분석')
    jobs = crawl_job_data(keyword)
    return jsonify(jobs)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)