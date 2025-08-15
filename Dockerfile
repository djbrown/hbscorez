FROM python:3.13-bookworm

RUN mkdir /code
WORKDIR /code

RUN pip install pipenv==2023.12.1
RUN apt update \
    && apt install -y --no-install-recommends default-jre fonts-liberation gsfonts locales \
    && apt clean \
    && rm -rf /var/lib/apt/lists/*

RUN echo "de_DE.UTF-8 UTF-8" >> /etc/locale.gen \
    && locale-gen

COPY Pipfile .
COPY Pipfile.lock .
RUN pipenv install --deploy
RUN pipenv install --skip-lock gunicorn==21.2.0

COPY entrypoint.sh .
COPY src/ src/

ENTRYPOINT ["./entrypoint.sh"]
