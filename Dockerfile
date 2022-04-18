FROM python:3.9
WORKDIR /drf_store
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY . .
