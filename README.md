# HbScorez

[![Travis-CI Build Status](https://travis-ci.org/djbrown/hbscorez.svg?branch=master)](https://travis-ci.org/djbrown/hbscorez)
[![Docker Build Status](https://img.shields.io/docker/build/djbrown/hbscorez.svg)](https://hub.docker.com/r/djbrown/hbscorez/builds/)
[![Coveralls Status](https://coveralls.io/repos/github/djbrown/hbscorez/badge.svg)](https://coveralls.io/github/djbrown/hbscorez)
[![codecov.io Status](https://codecov.io/github/djbrown/hbscorez/coverage.svg)](http://codecov.io/github/djbrown/hbscorez/)
[![Checked with mypy](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)
[![FOSSA Status](https://app.fossa.io/api/projects/git%2Bgithub.com%2Fdjbrown%2Fhbscorez.svg?type=shield)](https://app.fossa.io/projects/git%2Bgithub.com%2Fdjbrown%2Fhbscorez?ref=badge_shield)

This is the repo for the web application HbScorez running on https://hbscorez.de/.

HbScorez is a web application, which processes handball game reports of diverse handball associations, districts, and leagues. It analyzes the player scores and displays the statistics and rankings.

HbScorez is powered by Django

[<img src="https://www.djangoproject.com/m/img/logos/django-logo-positive.svg" height="50" alt="Django Logo"/>](https://www.djangoproject.com/)


## Running via Docker

`docker run -p 8001:8000 djbrown/hbscorez`<br/>
Container is reachable under [0.0.0.0:8001](http://0.0.0.0:8001)

## Running natively

### Requirements

1. python3
2. pipenv (`pip install pipenv`)
3. java (>=1.6) for parsing game report PDFs


### Installation

`pipenv install` (add `--dev` to include development dependencies)<br/>
`pipenv run python manage.py migrate`

### Start Application

`pipenv run python manage.py runserver`

## Testing

`pipenv run python manage.py test`

with coverage:<br/>
`pipenv run coverage run --branch --source=. --omit=*/migrations/* ./manage.py test`


## Main Commands

* **setup**: fetch associations, districts, seasons and leagues
* **import_games**: fetch games and sport halls
* **import_scores**: fetch players and scores

Execute Commands via `pipenv run python manage.py <COMMAD> <OPTIONS>`.<br/>
Prepend `docker run <CONTAINER> ` when running via Docker.<br/>
Append ` -h` to display Command help.



## License
[![FOSSA Status](https://app.fossa.io/api/projects/git%2Bgithub.com%2Fdjbrown%2Fhbscorez.svg?type=large)](https://app.fossa.io/projects/git%2Bgithub.com%2Fdjbrown%2Fhbscorez?ref=badge_large)

## Contribute
See [CONTRIBUTING.md](CONTRIBUTING.md)
