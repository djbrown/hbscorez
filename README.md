# HbScorez

[![Travis-CI Build Status](https://travis-ci.org/djbrown/hbscorez.svg?branch=master)](https://travis-ci.org/djbrown/hbscorez)
[![Docker Hub Build Status](https://img.shields.io/docker/build/djbrown/hbscorez.svg)](https://hub.docker.com/r/djbrown/hbscorez/builds/)
[![Coveralls Coverage Status](https://coveralls.io/repos/github/djbrown/hbscorez/badge.svg)](https://coveralls.io/github/djbrown/hbscorez)
[![Codecov Coverage Status](https://codecov.io/github/djbrown/hbscorez/coverage.svg)](http://codecov.io/github/djbrown/hbscorez/)
[![Codacy Quality Status](https://api.codacy.com/project/badge/Grade/aa168e5b5c154b1ba8b891afa0998d9e)](https://www.codacy.com/app/djbrown/hbscorez?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=djbrown/hbscorez&amp;utm_campaign=Badge_Grade)
[![Code Climate Maintainability](https://api.codeclimate.com/v1/badges/db7cf3c32bc124e21e8e/maintainability)](https://codeclimate.com/github/djbrown/hbscorez/maintainability)
[![Mypy Badge](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)
<!-- TODO: register on Sauce Labs at https://saucelabs.com/open-source/open-sauce [![Sauce Test Status](https://saucelabs.com/buildstatus/dan-brown)](https://saucelabs.com/u/dan-brown)
[![Sauce Labs Browsers](https://saucelabs.com/browser-matrix/dan-brown.svg)](https://saucelabs.com/u/dan-brown) -->
[![FOSSA License Status](https://app.fossa.io/api/projects/git%2Bgithub.com%2Fdjbrown%2Fhbscorez.svg?type=shield)](https://app.fossa.io/projects/git%2Bgithub.com%2Fdjbrown%2Fhbscorez?ref=badge_shield)
[![Updates](https://pyup.io/repos/github/djbrown/hbscorez/shield.svg)](https://pyup.io/repos/github/djbrown/hbscorez/)
[![Python 3](https://pyup.io/repos/github/djbrown/hbscorez/python-3-shield.svg)](https://pyup.io/repos/github/djbrown/hbscorez/)


<!-- TODO:  register on Sauce Labs at https://saucelabs.com/open-source/open-sauce [![Sauce Labs Browsers](https://saucelabs.com/browser-matrix/djbrown-hbscorez.svg)](https://saucelabs.com/u/djbrown-hbscorez) -->

This is the repo for the web application HbScorez running on https://hbscorez.de/.<br/>
HbScorez is a web application, which processes handball game reports of diverse handball associations, districts, and leagues.
It analyzes the player scores and displays the statistics and rankings.

HbScorez is powered by Django

[<img src="https://www.djangoproject.com/m/img/logos/django-logo-positive.svg" height="50" alt="Django Logo"/>](https://www.djangoproject.com/)


## Running via Docker

`docker run -p 8000:8000 djbrown/hbscorez:latest`<br/>
App is reachable under [127.0.0.1:8000](http://127.0.0.1:8000)


## Running natively

### Requirements
1. Python 3.7
2. pipenv (`pip install pipenv`)
3. Java (>=1.6) for parsing game report PDFs


### Installation
`pipenv install`<br/>
`pipenv run python src/manage.py migrate`

### Start Application
`pipenv run python src/manage.py runserver`


## Main Management Commands

* **setup**: fetch associations, districts, seasons and leagues
* **import_games**: fetch games and sport halls
* **import_reports**: fetch, parse and import game report data (players, scores, spectator count)

Execute commands via `pipenv run python src/manage.py <COMMAD> <OPTIONS>`.<br/>
Prepend `docker run djbrown/hbscorez:latest ` to execute inside Docker container.<br/>
Append ` -h` to display command help.


## License

The project is available as open source under the terms of the [MIT License](http://opensource.org/licenses/MIT).

[![FOSSA License Report](https://app.fossa.io/api/projects/git%2Bgithub.com%2Fdjbrown%2Fhbscorez.svg?type=large)](https://app.fossa.io/projects/git%2Bgithub.com%2Fdjbrown%2Fhbscorez?ref=badge_large)

## Contributing
See [CONTRIBUTING.md](.github/CONTRIBUTING.md)
