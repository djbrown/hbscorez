FROM python:3.6-stretch
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
RUN pip install pipenv
RUN apt-get update && apt-get install -y \
    default-jre \
    fonts-liberation \
    gsfonts
COPY Pipfile .
COPY Pipfile.lock .
RUN pipenv install
COPY . .

RUN ["pipenv", "run", "python", "manage.py", "migrate"]
RUN ["pipenv", "run", "python", "manage.py", "collectstatic --no-input"]
RUN ["pipenv", "run", "python", "manage.py", "setup"]
RUN ["pipenv", "run", "python", "manage.py", "download_reports"]
RUN ["pipenv", "run", "python", "manage.py", "import_scores"]

EXPOSE 8000
ENTRYPOINT ["pipenv", "run", "python", "manage.py", "runserver"]
CMD ["0.0.0.0:8000"]
