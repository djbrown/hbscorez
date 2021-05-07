# Code of Conduct

See [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)

# How to Contribute to Open Source

Want to contribute to open source?<br />
A guide to making open source contributions, for first-timers and for veterans:<br />
https://opensource.guide/

# Issues

The preferred way of giving feedback is via GitHub Issues.<br />
You should choose one of the [Issue Templates](https://github.com/djbrown/hbscorez/issues/new/choose)

# Forum

Alternatively, if you don't want to create an account on GitHub you can also use the public [QA Forum](https://redmine.djbrown.de/projects/hbscorez/boards) anonymously.

# Developing Python

## Package Management

If you want to add new dependencies to the project, make sure their license is compatible with the MIT license.
You can automatically generate attributions via `pipenv run pip-licenses -au --from classifier -f csv > ATTRIBUTIONS.csv`

This Project uses [Pipenv](https://github.com/pypa/pipenv/) for managing Python Packages.<br />
Install new dependencies from pypi via `pipenv install <PACKAGE>`.
Add `--dev` flag for development dependencies.

## Format and Style Guide

You can contribute to this Project using any IDE, Editor or Terminal you like, as long as your modifications obey the conventions defined by the [Style Guide for Python Code (PEP8)](https://www.python.org/dev/peps/pep-0008/).
The following command will clean your code accordingly: `pipenv run autopep8`

Also make sure to check messages from the following commands before proposing:

- `pipenv run mypy src`
- `pipenv run flake8`
- `pipenv run pylint src`

## Testing

### Test Modules

- are named `test_<module_name>.py`
- are run specifically via `pipenv run ./src/manage.py <module>`

### Test Cases

- are classes defined in a test module
- are named `Test<TestCaseName>`
- are run specifically via `pipenv run ./src/manage.py <module>.<TestCase>`

### Tests

- are methods or functions defined in test cases or test modules, respectively
- are named `test_<test_name>`
- are run specifically via `pipenv run ./src/manage.py <module>.<TestCase>.<test>`
- are run collectively via `pipenv run hbtest`

#### Unit Tests

- are isolated and do not connect to running components or external systems
- are defined in the `tests` subpackage of the related app
- are defined in test cases that subclass `django.test.TestCase`
- are run collectively via `pipenv run hbunittest`

##### Model Tests

- are like Unit Tests, but do connect to the local database
- are defined in test cases that subclass `base.tests.base.ModelTestCase`

#### Integration Tests

- are not isolated and do connect to running components or external systems
- are defined in the `tests.integration` subpackage of the related app
- are defined in test cases that subclass `base.tests.base.IntegrationTestCase`
- are run collectively via `pipenv run hbintegrationtest`

#### Selenium Tests

- are user centric and focus a single feature or functionality
- are defined in the `tests.selenium` subpackage of the related app
- are defined in test cases that subclass `base.tests.base.SeleniumTestCase`
- are run collectively via `pipenv run hbseleniumtest`
  - install [Firefox](https://www.mozilla.org/firefox/) and add to PATH
  - install [geckodriver](https://github.com/mozilla/geckodriver) and add to PATH
  - set Django setting `SELENIUM_TIMEOUT` according to the local processing and network power

### Coverage

- can be calculated by running tests via `pipenv run hbcoverage`
- can be reported as HTML after calculation via `pipenv run coverage html`
- can be reported as XML after calculation via `pipenv run coverage xml`

## JavaScript (:warning: Work in Progress)

<!-- TODO -->
