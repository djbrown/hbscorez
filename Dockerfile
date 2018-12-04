FROM python:3.7-stretch

RUN mkdir /code
WORKDIR /code

RUN pip install pipenv
RUN apt-get update && apt-get install -y \
    default-jre \
    fonts-liberation \
    gsfonts \
    locales
RUN echo "de_DE.UTF-8 UTF-8" >> /etc/locale.gen \
    && locale-gen

COPY Pipfile .
COPY Pipfile.lock .
RUN pipenv install gunicorn --skip-lock

COPY . .

ENTRYPOINT ["./entrypoint.sh"]
