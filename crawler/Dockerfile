# 베이스 이미지
FROM python:3.9-slim-buster

# 환경변수 설정 (Python 캐시파일 안 만들기)
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 작업 디렉토리 생성
WORKDIR /app

# 의존성 파일 먼저 복사 (캐시 최적화)
COPY requirements.txt .

# 패키지 설치
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# 전체 소스 복사
COPY . .

# 포트 노출
EXPOSE 5000

# 서버 실행 (Flask 개발 서버)
CMD ["python", "app.py"]