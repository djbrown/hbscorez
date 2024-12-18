# Contributing

The preferred way of contributing directly is by creating a [GitHub Fork](https://github.com/djbrown/hbscorez/fork).
You may setup and work on your fork according to the steps, respecting the following chapters of this guide.
Once the contribution is ready, you may propose a [GitHub Pull Request](https://github.com/djbrown/hbscorez/pulls).
The Pull Request will then be automatically checked agains every development policy automatically.
Also the Pull Request has to be reviewed by the maintainer and may receive some feedback to consider.
Once the Pull Request is successfully approved by the maintainer, it will be merged into the main branch.

Also here is a more general guide to making open source contributions, for first-timers and for veterans:  
[Open Source Guides](https://opensource.guide/)

## Package Management

If you want to add new dependencies to the project, make sure their license is compatible with the MIT license.

This Project uses [Pipenv](https://github.com/pypa/pipenv/) for managing Python Packages.  
Install new dependencies from pypi via `pipenv install <PACKAGE>`.
Add `--dev` flag for development dependencies.

## Code Formatting and Style Guide

You may contribute to this Project using any IDE, Editor or Terminal you like, as long as your modifications obey the conventions defined by the [Style Guide for Python Code (PEP8)](https://www.python.org/dev/peps/pep-0008/).
The following commands will format your code accordingly:

- format code: `pipenv run black src`
- sort imports: `pipenv run isort src`

Also make sure to check messages from the following linter commands before proposing:

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
- are defined in the `tests.unit` subpackage of the related app
- are defined in test cases that subclass `django.test.TestCase`
- are run collectively via `pipenv run hbunittest`

##### Model Tests

- are Unit Tests, that connect to the local database
- are defined in test cases that subclass `base.tests.base.ModelTestCase`

#### Integration Tests

- are not isolated and do connect to running components or external systems
- are defined in the `tests.integration` subpackage of the related app
- are defined in test cases that subclass `base.tests.base.IntegrationTestCase`
- are run collectively via `pipenv run hbintegrationtest`

#### Browser Tests

- are user centric and focus a single feature or functionality
- are implemented with [Selenium](https://www.selenium.dev/)
- are defined in the `tests.browser` subpackage of the related app
- are defined in test cases that subclass `base.tests.base.BrowserTestCase`
- are run collectively via `pipenv run hbbrowsertest`
  - install [Firefox](https://www.mozilla.org/firefox/) and add to PATH
  - install [geckodriver](https://github.com/mozilla/geckodriver) and add to PATH
  - set Django setting `BROWSER_TIMEOUT` according to the processing and network power of the browser platform

### Coverage

- may be calculated by running tests via `pipenv run hbcoverage`
- may be reported as HTML after calculation via `pipenv run coverage html`
- may be reported as XML after calculation via `pipenv run coverage xml`
