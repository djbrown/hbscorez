FROM python:3-stretch
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN apt-get update && apt-get install -y \
    default-jre \
    fonts-liberation \
    gsfonts
COPY . .
CMD sh run.sh
