#!/bin/sh
##
## SPDX-FileCopyrightText: 2020 Splunk, Inc. <sales@splunk.com>
## SPDX-License-Identifier: LicenseRef-Splunk-1-2020
##
##

cd /home/circleci/work
if [ -f "${TEST_SET}/pytest-ci.ini" ]; then
    cp -f ${TEST_SET}/pytest-ci.ini pytest.ini
fi

pip install -r requirements_dev.txt
pip install six>=1.15
pip install git+https://github.com/rfaircloth-splunk/agent-python-pytest.git

cp -f .pytest.expect ${TEST_SET}

echo "Executing Tests..."
RERUN_COUNT=${RERUN_COUNT:-1}
if [ -z ${TEST_BROWSER} ] 
then
    echo Test Args $@ ${TEST_SET}
    pytest $@ ${TEST_SET}
    test_exit_code=$?
else
    # Execute the tests on Headless mode in local if UI_TEST_HEADLESS environment is set to "true"
    if [ "${UI_TEST_HEADLESS}" = "true" ]
    then
        echo Test Args $@ --local --persist-browser --headless --reruns=${RERUN_COUNT} --browser=${TEST_BROWSER}\
        ${TEST_SET} 
        
        pytest $@ --local --persist-browser --headless --reruns=${RERUN_COUNT} --browser=${TEST_BROWSER} \
        ${TEST_SET}
        test_exit_code=$?
    else
        echo "Check Saucelab connection..."
        wget --retry-connrefused --no-check-certificate -T 10 sauceconnect:4445
        sauce_connect_connection=$?
        echo "Sauce Connect Status:$sauce_connect_connection"
        [ "$sauce_connect_connection" -eq "4" ] && echo "SauceConnect is not running. Exiting the tests...." && exit 1
        echo Test Args $@ --reruns=${RERUN_COUNT} --browser=${TEST_BROWSER} ${TEST_SET}
        pytest $@ --reruns=${RERUN_COUNT} --browser=${TEST_BROWSER} \
        ${TEST_SET}
        test_exit_code=$?
    fi
fi
exit "$test_exit_code" 
