# SPDX-FileCopyrightText: 2020 Splunk Inc (Ryan Faircloth) <rfaircloth@splunk.com>
#
# SPDX-License-Identifier: Apache-2.0

import os
import pytest


def pytest_configure(config):
    config.addinivalue_line("markers", "external: Test search time only")
    config.addinivalue_line("markers", "docker: Test search time only")


@pytest.fixture(scope="session")
def docker_compose_files(request):
    """
    Get an absolute path to the  `docker-compose.yml` file. Override this
    fixture in your tests if you need a custom location.
    Returns:
        string: the path of the `docker-compose.yml` file
    """
    docker_compose_path = os.path.join(
        str(request.config.invocation_dir), "docker-compose.yml"
    )
    # LOGGER.info("docker-compose path: %s", docker_compose_path)

    return [docker_compose_path]


def pytest_addoption(parser):
    group = parser.getgroup("seckit-geolocation")
    
    MAXMIND_ACCOUNT = os.getenv('MAXMIND_ACCOUNT')
    MAXMIND_KEY = os.getenv('MAXMIND_KEY')
    if MAXMIND_ACCOUNT is None:
        MAXMIND_ACCOUNT = "1111" 
    if MAXMIND_KEY is None:
        MAXMIND_KEY = "invalid" 
    group.addoption(
        "--maxmind_id",
        action="store",
        dest="maxmind_id",
        default=MAXMIND_ACCOUNT,
        help="Numeric ID assigned by maxmind",
    )
    
    group.addoption(
        "--maxmind_password",
        action="store",
        dest="maxmind_password",
        default=MAXMIND_KEY,
        help="Key for the license ID used as password",
    )


@pytest.fixture(scope="session")
def seckit_input(splunk_rest_uri, request):

    payload = {
        "name": "main",
        "output_mode": "json",
        "username": request.config.getoption("maxmind_id"),
        "password": request.config.getoption("maxmind_password"),
    }

    splunk_rest_uri[0].post(
        f"{splunk_rest_uri[1]}servicesNS/nobody/SecKit_SA_geolocation/SecKit_SA_geolocation_account/create",
        data=payload,
        verify=False,
    ).status_code

    splunk_rest_uri[0].post(
        f"{splunk_rest_uri[1]}servicesNS/nobody/SecKit_SA_geolocation/SecKit_SA_geolocation_geoipupdate/main?output_mode=json",
        data={"disabled": "0"},
        verify=False,
    ).status_code
