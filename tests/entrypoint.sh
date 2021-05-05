#!/bin/sh
##
## SPDX-FileCopyrightText: 2021 Splunk, Inc. <sales@splunk.com>
## SPDX-License-Identifier: LicenseRef-Splunk-1-2020
##
##

cd /home/circleci/work
pip install pip==20.2
if [ -f "${TEST_SET}/pytest-ci.ini" ]; then
    cp -f ${TEST_SET}/pytest-ci.ini pytest.ini
fi

# Installing the lib folder inside requirements for unit test case stage
if [ "${TEST_TYPE}" = "unit" ]
then
    [ "${IMAGE_TAG}" = "2.7.17" ] && FOLDER_NAME="py2" || FOLDER_NAME="py3"
    if [ -f "package/lib/requirements.txt" ]; then
        pip install -r package/lib/requirements.txt --user
    fi
    if [ -f "package/lib/${FOLDER_NAME}/requirements.txt" ]; then
        pip install -r package/lib/${FOLDER_NAME}/requirements.txt --user
    fi
fi

if [ "${IMAGE_TAG}" = "2.7.17" ]
then
    pip install -r requirements_py2_dev.txt
    pip install six>=1.15
else
    pip install -r requirements_dev.txt --user
    pip install six>=1.15 --user
    pip install git+https://github.com/rfaircloth-splunk/agent-python-pytest.git --user
fi

cp -f .pytest.expect ${TEST_SET}

echo "Executing Tests..."
RERUN_COUNT=${RERUN_COUNT:-1}
if [ -z ${TEST_BROWSER} ] 
then
    echo Test Args $@ --reportportal -o "rp_endpoint=${RP_ENDPOINT}" -o "rp_launch_attributes=${RP_LAUNCH_ATTRIBUTES}" \
    -o "rp_project=${RP_PROJECT}" -o "rp_launch=${RP_LAUNCH}" -o "rp_launch_description='${RP_LAUNCH_DESC}'" -o "rp_ignore_attributes='xfail' 'usefixture'" \
    ${TEST_SET}     
    if [ "${IMAGE_TAG}" = "2.7.17" ]
    then
        pytest $@ \
        ${TEST_SET} 
        test_exit_code=$?
    else
        pytest $@ \
        --reportportal -o "rp_endpoint=${RP_ENDPOINT}" -o "rp_launch_attributes=${RP_LAUNCH_ATTRIBUTES}" \
        -o "rp_project=${RP_PROJECT}" -o "rp_launch=${RP_LAUNCH}" -o "rp_launch_description='${RP_LAUNCH_DESC}'" -o "rp_ignore_attributes='xfail' 'usefixture'" \
        ${TEST_SET}
        test_exit_code=$?
    fi
else
    # Execute the tests on Headless mode in local if UI_TEST_HEADLESS environment is set to "true"
    if [ "${UI_TEST_HEADLESS}" = "true" ]
    then
        echo Test Args $@ --local --persist-browser --headless --reruns=${RERUN_COUNT} --browser=${TEST_BROWSER}\
        --reportportal -o "rp_endpoint=${RP_ENDPOINT}" -o "rp_launch_attributes=${RP_LAUNCH_ATTRIBUTES}" \
        -o "rp_project=${RP_PROJECT}" -o "rp_launch=${RP_LAUNCH}" -o "rp_launch_description='${RP_LAUNCH_DESC}'" -o "rp_ignore_attributes='xfail' 'usefixture'" \
        ${TEST_SET} 
        
        pytest $@ --local --persist-browser --headless --reruns=${RERUN_COUNT} --browser=${TEST_BROWSER} \
        --reportportal -o "rp_endpoint=${RP_ENDPOINT}" -o "rp_launch_attributes=${RP_LAUNCH_ATTRIBUTES}" \
        -o "rp_project=${RP_PROJECT}" -o "rp_launch=${RP_LAUNCH}" -o "rp_launch_description='${RP_LAUNCH_DESC}'" -o "rp_ignore_attributes='xfail' 'usefixture'" \
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
        --reportportal -o "rp_endpoint=${RP_ENDPOINT}" -o "rp_launch_attributes=${RP_LAUNCH_ATTRIBUTES}" \
        -o "rp_project=${RP_PROJECT}" -o "rp_launch=${RP_LAUNCH}" -o "rp_launch_description='${RP_LAUNCH_DESC}'" -o "rp_ignore_attributes='xfail' 'usefixture'" \
        ${TEST_SET}
        test_exit_code=$?
    fi
fi
exit "$test_exit_code" 