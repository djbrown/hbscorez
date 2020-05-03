#  Code of Conduct
See [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)

# How to Contribute to Open Source
Want to contribute to open source?<br/>
A guide to making open source contributions, for first-timers and for veterans:<br/>
https://opensource.guide/

# Issues
The preferred way of giving feedback is via GitHub Issues.<br/>
You should choose one of the [Issue Templates](https://github.com/djbrown/hbscorez/issues/new/choose)

# Forum
Alternatively, if you don't want to create an account on GitHub you can also use the public [QA Forum](https://redmine.djbrown.de/projects/hbscorez/boards) anonymously.

# Developing Python

## Package Management
If you want to add new dependencies to the project, make sure their license is compatible with the MIT license.
You can automatically generate attributions via `pipenv run pip-licenses -sau --from classifier -f csv > ATTRIBUTIONS.csv`

This Project uses [Pipenv](https://github.com/pypa/pipenv/) for managing Python Packages.<br/>
Install new dependencies from pypi via `pipenv install <PACKAGE>`.
Add `--dev` flag for development dependencies.

:warning: pylint is currenctly not installable via pipenv (see pypa/pipenv#2284 and pypa/pipenv#3827)
In order to use pylint you have to run `pipenv install --dev --skip-lock pylint pylint-django`

## Style Guide
You can contribute to this Project using any IDE, Editor or Terminal you like, as long as your modifications obey the conventions defined by the [Style Guide for Python Code (PEP8)](https://www.python.org/dev/peps/pep-0008/).
The following command will clean your code accordingly: `pipenv run autopep8`

Also make sure to check messages from the following commands before proposing:
* `pipenv run mypy src`
* `pipenv run flake8`

### Testing
Run tests: `pipenv run hbtest`<br/>
Run coverage: `pipenv run hbcoverage`

#### Test Modules
* A test module is a module that tests a single source module.
* A test module is defined in in the `tests` subpackage of the related app.
* A test module is named `test_<module_name>.py`.

#### Test Cases
* A test case is a class that tests a single source class.
* A test case is defined in a test module.
* A test case is named `Test<TestCaseName>`
* A test case subclasses `django.test.TestCase`

#### Tests
* A test is a method that tests a single source function or method.
* A test is defined in a test case.
* A test is named `test_<test_name>`.

#### Test Scenarios
* A test scenario ist a tuple of given input(s) and expected output or behaviour for a source function or method.
* A test scenario is defined within an unparametrized test or annotated on a parametrized test.

#### Selenium Test Cases
* A selenium test case is used to assert a single integrational server client interaction.
* A selenium test module is defined in the `tests.selenium` subpackage of the related app.
* A selenium test case subclasses `base.tests.base.SeleniumTestCase`.
* A selenium test case is only run in CI.
* A selenium test case can be run locally:
  * install [Firefox](https://www.mozilla.org/firefox/) and add to PATH
  * install [geckodriver](https://github.com/mozilla/geckodriver) and add to PATH
  * set Django setting `SELENIUM_TIMEOUT` according to the local processing power
  * `./src/manage.py test --tag selenium src`

## JavaScript (:warning: Work in Progress)
<!-- TODO -->
