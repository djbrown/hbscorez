#!/bin/bash

travis_fold start unit-test-coverage
echo "$ pipenv run hbcoverage"
pipenv run hbcoverage
travis_fold end unit-test-coverage

if [ "$TRAVIS_EVENT_TYPE" = "cron" ]
then
    travis_fold start integration-test
    echo "$ pipenv run hbintegrationtest"
    pipenv run hbintegrationtest
    travis_fold end integration-test

    travis_fold start selenium-test
    echo "$ pipenv run hbseleniumtest"
    pipenv run hbseleniumtest
    travis_fold end selenium-test
fi
