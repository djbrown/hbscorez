# HbScorez

[![CI Build](https://github.com/djbrown/hbscorez/actions/workflows/ci-build.yml/badge.svg)](https://github.com/djbrown/hbscorez/actions/workflows/ci-build.yml)
[![Nightly Build](https://github.com/djbrown/hbscorez/actions/workflows/nightly-build.yml/badge.svg)](https://github.com/djbrown/hbscorez/actions/workflows/nightly-build.yml)
[![Docker Image Version (latest semver)](https://img.shields.io/docker/v/djbrown/hbscorez?label=image&sort=semver)](https://hub.docker.com/r/djbrown/hbscorez)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=djbrown_hbscorez&metric=alert_status)](https://sonarcloud.io/dashboard?id=djbrown_hbscorez)
[![Coveralls Coverage Status](https://coveralls.io/repos/github/djbrown/hbscorez/badge.svg)](https://coveralls.io/github/djbrown/hbscorez)
[![Codecov Coverage Status](https://codecov.io/github/djbrown/hbscorez/coverage.svg)](https://codecov.io/github/djbrown/hbscorez/)
[![Codacy Quality Status](https://api.codacy.com/project/badge/Grade/aa168e5b5c154b1ba8b891afa0998d9e)](https://www.codacy.com/app/djbrown/hbscorez?utm_source=github.com&utm_medium=referral&utm_content=djbrown/hbscorez&utm_campaign=Badge_Grade)
[![Codacy Coverage Status](https://app.codacy.com/project/badge/Coverage/aa168e5b5c154b1ba8b891afa0998d9e)](https://www.codacy.com/manual/djbrown/hbscorez/dashboard?utm_source=github.com&utm_medium=referral&utm_content=djbrown/hbscorez&utm_campaign=Badge_Coverage)
[![Code Climate Maintainability](https://api.codeclimate.com/v1/badges/db7cf3c32bc124e21e8e/maintainability)](https://codeclimate.com/github/djbrown/hbscorez/maintainability)
[![Code Climate Test Coverage](https://api.codeclimate.com/v1/badges/db7cf3c32bc124e21e8e/test_coverage)](https://codeclimate.com/github/djbrown/hbscorez/test_coverage)
[![CodeScene Code Health](https://codescene.io/projects/40238/status-badges/code-health)](https://codescene.io/projects/40238)
[![Mypy Badge](https://www.mypy-lang.org/static/mypy_badge.svg)](https://mypy-lang.org/)
[![Sauce Test Status](https://saucelabs.com/buildstatus/dan-brown)](https://saucelabs.com/u/dan-brown)
[![FOSSA License Status](https://app.fossa.com/api/projects/custom%2B5488%2Fgithub.com%2Fdjbrown%2Fhbscorez.svg?type=shield)](https://app.fossa.com/projects/custom%2B5488%2Fgithub.com%2Fdjbrown%2Fhbscorez?ref=badge_shield)

This is the repo for the web application HbScorez running [hbscorez.de](https://hbscorez.de/).  
HbScorez processes handball game reports of diverse handball associations, districts, and leagues.
It analyzes the player scores and displays the statistics and rankings.

## Project Management and Issue Tracking

**[redmine.djbrown.de](https://redmine.djbrown.de/projects/hbscorez)**

## Acknowledgements

HbScorez is powered by **Django**  
[<img src="https://www.djangoproject.com/m/img/logos/django-logo-positive.svg" height="50" alt="Django Logo"/>](https://www.djangoproject.com/)

## Running via Docker

`docker run -p 8000:8000 djbrown/hbscorez:latest`  
App is reachable under [127.0.0.1:8000](http://127.0.0.1:8000)

## Running natively

### Requirements

1. Python 3.10
1. pipenv (`pip install pipenv`)
1. Java (>=1.6) for parsing game report PDFs

### Installation

`pipenv install`  
`pipenv run ./src/manage.py migrate`

### Start Application

`pipenv run ./src/manage.py runserver`

## Main Management Commands

- `import_associations`: Associations
- `import_districts`: Districts
- `import_leagues`: Seasons, Leagues, Teams
- `import_games`: Games, Sport Halls
- `import_reports`: Players, Scores

Execute commands via `pipenv run ./src/manage.py <COMMAD> <OPTIONS>`.  
Prepend `docker run djbrown/hbscorez:latest ` to execute inside Docker container.  
Append ` -h` to display command help.

## License

The project is available as open source under the terms of the [MIT License](https://opensource.org/licenses/MIT).

[![FOSSA License Report](https://app.fossa.com/api/projects/custom%2B5488%2Fgithub.com%2Fdjbrown%2Fhbscorez.svg?type=large)](https://app.fossa.com/projects/custom%2B5488%2Fgithub.com%2Fdjbrown%2Fhbscorez?ref=badge_large)
[![Sauce Labs Browsers](https://saucelabs.com/browser-matrix/dan-brown.svg)](https://saucelabs.com/u/dan-brown)

## Contributing

See [CONTRIBUTING.md](.github/CONTRIBUTING.md)
