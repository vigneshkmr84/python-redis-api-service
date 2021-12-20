#FROM python:3.6
FROM python:3.6-slim-buster

COPY dependencies.txt dependencies.txt
RUN pip install -r dependencies.txt

COPY app.py /opt/app/
EXPOSE 5000
CMD ["python", "/opt/app/app.py"]


