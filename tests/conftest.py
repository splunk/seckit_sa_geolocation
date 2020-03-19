import pytest


def pytest_addoption(parser):
    group = parser.getgroup("seckit-geolocation")

    group.addoption(
        "--maxmind_id",
        action="store",
        dest="maxmind_id",
        default="1111",
        help="Numeric ID assigned by maxmind",
    )
    group.addoption(
        "--maxmind_password",
        action="store",
        dest="maxmind_password",
        default="none",
        help="Key for the license ID used as password",
    )


@pytest.fixture(scope="session")
def seckit_input(splunk_rest, request):

    payload = {
        'name': 'main',
        'output_mode': 'json',
        'username': request.config.getoption("maxmind_id"),
        'password': request.config.getoption("maxmind_password")
    }

    splunk_rest[0].post(f'{splunk_rest[1]}servicesNS/nobody/SecKit_SA_geolocation/SecKit_SA_geolocation_account/create',
                        data=payload, verify=False).status_code

    splunk_rest[0].post(f'{splunk_rest[1]}servicesNS/nobody/SecKit_SA_geolocation/SecKit_SA_geolocation_geoipupdate/main?output_mode=json',
                        data={'disabled': '0'}, verify=False).status_code
