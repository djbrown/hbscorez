# HbScorez

[![Travis-CI Build Status](https://travis-ci.org/djbrown/hbscorez.svg?branch=master)](https://travis-ci.org/djbrown/hbscorez)
[![Docker Build Status](https://img.shields.io/docker/build/djbrown/hbscorez.svg)](https://hub.docker.com/r/djbrown/hbscorez/builds/)
[![Coveralls Status](https://coveralls.io/repos/github/djbrown/hbscorez/badge.svg)](https://coveralls.io/github/djbrown/hbscorez)
[![codecov.io Status](https://codecov.io/github/djbrown/hbscorez/coverage.svg)](http://codecov.io/github/djbrown/hbscorez/)
[![FOSSA Status](https://app.fossa.io/api/projects/git%2Bgithub.com%2Fdjbrown%2Fhbscorez.svg?type=shield)](https://app.fossa.io/projects/git%2Bgithub.com%2Fdjbrown%2Fhbscorez?ref=badge_shield)

This is the repo for the web application HbScorez running on https://hbscorez.de/.

HbScorez is a web application, which processes handball game reports of diverse handball associations, districts, and leagues. It analyzes the player scores and displays the statistics and rankings.

HbScorez is powered by Django

[<img src="https://www.djangoproject.com/m/img/logos/django-logo-positive.svg" height="50" alt="Django Logo"/>](https://www.djangoproject.com/)


## Requirements

* python3
* java (>=1.6)
* pipenv (`$ pip install pipenv`)


## Installation

`$ pipenv install` (add `--dev` to include development dependencies)

`$ pipenv run python manage.py migrate`


## Testing

`$ pipenv run python manage.py migrate`

with coverage:<br/>
`$ pipenv run coverage run --branch --source=. --omit=*/migrations/* ./manage.py test`



## Initialize Data

`$ pipenv run python manage.py setup` ¹

`$ pipenv run python manage.py import_games` ¹

`$ pipenv run python manage.py import_scores` ¹

¹) add `-h` to display help message


## Start Application

`$ pipenv run python manage.py runserver`


## License
[![FOSSA Status](https://app.fossa.io/api/projects/git%2Bgithub.com%2Fdjbrown%2Fhbscorez.svg?type=large)](https://app.fossa.io/projects/git%2Bgithub.com%2Fdjbrown%2Fhbscorez?ref=badge_large)

## Contribute
See [CONTRIBUTING.md](CONTRIBUTING.md)
