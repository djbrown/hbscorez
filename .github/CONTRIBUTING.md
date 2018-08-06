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

This Project uses [Pipenv](https://github.com/pypa/pipenv/) for managing Python Packages.<br/>
If you want to modify the code creating

## Style Guide

You can contribute to this Project using any IDE, Editor or Terminal you like, as long as your modifications obey the conventions defined by the [Style Guide for Python Code (PEP8)](https://www.python.org/dev/peps/pep-0008/).
The following command will clean your code accordingly: `pipenv run autopep8`

Also make sure to check messages from the following commands before proposing:
* `pipenv run mypy hbscorez`
* `pipenv run flake8`
