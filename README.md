# HbScorez

[![Travis-CI Build Status](https://app.travis-ci.com/djbrown/hbscorez.svg?branch=master)](https://app.travis-ci.com/djbrown/hbscorez)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=djbrown_hbscorez&metric=alert_status)](https://sonarcloud.io/dashboard?id=djbrown_hbscorez)
[![Coveralls Coverage Status](https://coveralls.io/repos/github/djbrown/hbscorez/badge.svg)](https://coveralls.io/github/djbrown/hbscorez)
[![Codecov Coverage Status](https://codecov.io/github/djbrown/hbscorez/coverage.svg)](http://codecov.io/github/djbrown/hbscorez/)
[![Codacy Quality Status](https://api.codacy.com/project/badge/Grade/aa168e5b5c154b1ba8b891afa0998d9e)](https://www.codacy.com/app/djbrown/hbscorez?utm_source=github.com&utm_medium=referral&utm_content=djbrown/hbscorez&utm_campaign=Badge_Grade)
[![Codacy Coverage Status](https://app.codacy.com/project/badge/Coverage/aa168e5b5c154b1ba8b891afa0998d9e)](https://www.codacy.com/manual/djbrown/hbscorez/dashboard?utm_source=github.com&utm_medium=referral&utm_content=djbrown/hbscorez&utm_campaign=Badge_Coverage)
[![Code Climate Maintainability](https://api.codeclimate.com/v1/badges/db7cf3c32bc124e21e8e/maintainability)](https://codeclimate.com/github/djbrown/hbscorez/maintainability)
[![Code Climate Test Coverage](https://api.codeclimate.com/v1/badges/db7cf3c32bc124e21e8e/test_coverage)](https://codeclimate.com/github/djbrown/hbscorez/test_coverage)
[![Mypy Badge](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)

<!-- TODO: register on Sauce Labs at https://saucelabs.com/open-source/open-sauce [![Sauce Test Status](https://saucelabs.com/buildstatus/dan-brown)](https://saucelabs.com/u/dan-brown)
[![Sauce Labs Browsers](https://saucelabs.com/browser-matrix/dan-brown.svg)](https://saucelabs.com/u/dan-brown) -->

[![FOSSA License Status](https://app.fossa.com/api/projects/custom%2B5488%2Fgithub.com%2Fdjbrown%2Fhbscorez.svg?type=shield)](https://app.fossa.com/projects/custom%2B5488%2Fgithub.com%2Fdjbrown%2Fhbscorez?ref=badge_shield)
[![Updates](https://pyup.io/repos/github/djbrown/hbscorez/shield.svg)](https://pyup.io/repos/github/djbrown/hbscorez/)
[![Python 3](https://pyup.io/repos/github/djbrown/hbscorez/python-3-shield.svg)](https://pyup.io/repos/github/djbrown/hbscorez/)

<!-- TODO:  register on Sauce Labs at https://saucelabs.com/open-source/open-sauce [![Sauce Labs Browsers](https://saucelabs.com/browser-matrix/djbrown-hbscorez.svg)](https://saucelabs.com/u/djbrown-hbscorez) -->

This is the repo for the web application HbScorez running https://hbscorez.de/.<br/>
HbScorez processes handball game reports of diverse handball associations, districts, and leagues.
It analyzes the player scores and displays the statistics and rankings.

## Acknowledgements

HbScorez is powered by **Django**<br/>
[<img src="https://www.djangoproject.com/m/img/logos/django-logo-positive.svg" height="50" alt="Django Logo"/>](https://www.djangoproject.com/)

[ ~ Dependencies scanned by **PyUp.io** ~ ]<br/>
[<img src="https://pyup.io/static/images/logo.png" height="50"/>](https://pyup.io/)

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
`pipenv run ./src/manage.py migrate`

### Start Application

`pipenv run ./src/manage.py runserver`

## Main Management Commands

- **setup**: fetch associations, districts, seasons and leagues
- **import_games**: fetch games and sport halls
- **import_reports**: fetch, parse and import game report data (players, scores, spectator count)

Execute commands via `pipenv run ./src/manage.py <COMMAD> <OPTIONS>`.<br/>
Prepend `docker run djbrown/hbscorez:latest ` to execute inside Docker container.<br/>
Append ` -h` to display command help.

## License

The project is available as open source under the terms of the [MIT License](http://opensource.org/licenses/MIT).

[![FOSSA License Report](https://app.fossa.com/api/projects/custom%2B5488%2Fgithub.com%2Fdjbrown%2Fhbscorez.svg?type=large)](https://app.fossa.com/projects/custom%2B5488%2Fgithub.com%2Fdjbrown%2Fhbscorez?ref=badge_large)

## Contributing

See [CONTRIBUTING.md](.github/CONTRIBUTING.md)
