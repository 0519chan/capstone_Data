# Dockerfile
FROM python:3.9

WORKDIR /app
COPY . .
RUN pip install -r requirements.txt

EXPOSE 4040

CMD ["python", "app.py"]