FROM python:3.10-slim-buster

ENV YAYA_API_URL=https://yayawallet.com/api/en
ENV YAYA_API_PATH=/api/en
ENV YAYA_API_KEY=key-test_19aca8ac-7925-4438-9ece-e54b6fc31d61
ENV YAYA_API_SECRET=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJhcGlfa2V5Ijoia2V5LXRlc3RfMTlhY2E4YWMtNzkyNS00NDM4LTllY2UtZTU0YjZmYzMxZDYxIiwic2VjcmV0IjoiM2QwMWU3ZTcxNDVkYTRhY2RlMmM2MzA3NzRhMjFjODU0ZmFkNzIwZCJ9.-Zy7J39-3VIlmtr-6ROpF2nN1b0C5Dzh7iOc2rdzXbQ

WORKDIR /app

COPY requirements.txt /app/requirements.txt

RUN pip install -r requirements.txt

COPY . /app

EXPOSE 8000

ENTRYPOINT ["python3"] 
CMD ["manage.py", "runserver", "0.0.0.0:8000"]