FROM python:3.12-alpine3.20

COPY . ./requirements.txt
RUN pip install -r requirements.txt
COPY . .
