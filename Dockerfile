FROM python:3.10-bullseye

RUN mkdir /code
WORKDIR /code

RUN pip install pipenv==2022.1.8
RUN apt-get update \
    && apt-get install -y --no-install-recommends default-jre fonts-liberation gsfonts locales \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN echo "de_DE.UTF-8 UTF-8" >> /etc/locale.gen \
    && locale-gen

COPY Pipfile .
COPY Pipfile.lock .
RUN pipenv install --deploy
RUN pipenv install --skip-lock gunicorn==20.1.0

COPY entrypoint.sh .
COPY src/ src/

ENTRYPOINT ["./entrypoint.sh"]
