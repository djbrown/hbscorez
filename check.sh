#!/bin/env bash

set -e

pipenv run black src --check
pipenv run isort src --check
pipenv run flake8
pipenv run pylint src
pipenv run mypy src --check-untyped-defs
pipenv run hbunittest
