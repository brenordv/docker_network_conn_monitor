FROM python:3.7.6-stretch

COPY ./app /app
WORKDIR /app

RUN pip install -r ./requirements.txt

CMD ["python", "conn_monitor.py"]