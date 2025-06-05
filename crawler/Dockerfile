FROM python:3.9-slim-buster

# 캐시 설정
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/root/.local/bin:$PATH"

# 작업 디렉토리
WORKDIR /app

# requirements 먼저 복사 및 설치
COPY requirements.txt .

RUN pip install --upgrade pip && pip install -r requirements.txt


# 소스 전체 복사
COPY . .

# 포트 노출
EXPOSE 5000

# 서버 실행
CMD ["python", "-m", "uvicorn", "app:fast_app", "--host", "0.0.0.0", "--port", "5000"]
