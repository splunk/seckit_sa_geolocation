
# Run Addon tests in local environment

## With Docker

### Prerequisitory - Docker
- Git
- Python3 (>=3.7)
- Python2
- crudini
- Docker
- Docker-compose

### Steps - Docker

1. Clone the repository
```bash
git clone git@github.com:splunk/<repo name>.git
cd <repo dir>
git submodule update --init --recursive
```

2. Install Requirements and Generate Addon
```bash
pip3 install -r requirements_dev.txt
ucc-gen

# Execute only if TEST_TYPE is modinput_functional or modinput_others
curl -s https://api.github.com/repos/splunk/splunk-add-on-for-modinput-test/releases/latest | grep "Splunk_TA.*tar.gz" | grep -v search_head | grep -v indexer | grep -v forwarder | cut -d : -f 2,3 | tr -d \" | wget -qi -; tar -xvzf *.tar.gz -C deps/apps/
```

3. Set Variables
```bash
export SPLUNK_VERSION=<splunk_version> [i.e. latest, 8.1.0]
export SPLUNK_APP_ID=$(crudini --get package/default/app.conf id name) [i.e. Splunk_TA_addon-name]
export SPLUNK_APP_PACKAGE=output/$(ls output/) [i.e. output/Splunk_TA_addon-name]
export TEST_TYPE=<knowledge|ui|modinput_functional|modinput_others>
export TEST_SET=tests/$TEST_TYPE [i.e. tests/knowledge]
export IMAGE_TAG="3.7-browsers"
export SC4S_VERSION=<sc4s_version> [i.e. latest, 1.51.0]

# If TEST_TYPE is ui also set the following variables
export TEST_BROWSER=<browser_name> [i.e. chrome, firefox]
export JOB_NAME=<LocalRun::[addon_name]-[browser]>
export SAUCE_USERNAME=<sauce_username>
export SAUCE_PASSWORD=<sauce_password>
export SAUCE_IDENTIFIER=$SAUCE_IDENTIFIER-$(cat /proc/sys/kernel/random/uuid)
export UI_TEST_HEADLESS="true"
```
**Note:** If TEST_TYPE is `modinput_functional`, `modinput_others` or `ui`, also set all variables in [test_credentials.env](test_credentials.env) file with appropriate values encoded with base64.

4. Docker Build and test execution
```bash
docker-compose -f docker-compose.yml build

# Execute only if TEST_TYPE is ui
[ -z $BROWSER ] || [ "$UI_TEST_HEADLESS" = "true" ] || docker-compose -f docker-compose.yml up -d sauceconnect

docker-compose -f docker-compose.yml up -d splunk
until docker-compose -f docker-compose.yml logs splunk | grep "Ansible playbook complete" ; do sleep 1; done
docker-compose -f docker-compose.yml up --abort-on-container-exit test
```


## With External

### Prerequisitory - external
- Git
- Python3 (>=3.7)
- Python2
- Splunk along with addon installed and HEC token created
- If Addon support the syslog data ingestion(sc4s)
  - Docker
  - Docker-compose

### Steps - external

1. Clone the repository
```bash
git clone git@github.com:splunk/<repo name>.git
cd <repo dir>
git submodule update --init --recursive
```

2. Install Requirements
```bash
pip3 install -r requirements_dev.txt
```

3. Set Variables (only if Addon supports sc4s)

**Note:** Stop the existing splunk if it is running. New splunk will up after executing following steps with `Changed@11` splunk password.
```bash
export SPLUNK_VERSION=<splunk_version> [i.e. latest, 8.1.0]
export SPLUNK_APP_ID=<Addon_id> [i.e. Splunk_TA_addon-name]
export SPLUNK_APP_PACKAGE=<splunk_package>
export IMAGE_TAG="3.7-browsers"
export SC4S_VERSION=<sc4s_version>

docker-compose -f docker-compose.yml build
docker-compose -f docker-compose.yml up -d splunk
```

4. Run Tests

- Knowledge

```bash
pytest -vv --splunk-type=external --splunk-app=<path-to-addon-package> --splunk-data-generator=<path to pytest-splunk-addon-data.conf file> --splunk-host=<hostname> --splunk-port=<splunk-management-port> --splunk-user=<username> --splunk-password=<password> --splunk-hec-token=<splunk_hec_token> --sc4s-host=<sc4s_host> --sc4s-port=<sc4s_port>
```

- UI

1. Set all variables in environment mentioned at [test_credentials.env](test_credentials.env) file with appropriate values encoded with base64.
2. Download Browser's specific driver
    - For Chrome: download chromedriver
    - For Firefox: download geckodriver
    - For IE: download IEdriverserver
3. Put the downloaded driver into `test/ui/` directory, make sure that it is within the environment's PATH variable, and that it is executable
4. For Internet explorer, The steps mentioned at below link must be performed [selenium](https://github.com/SeleniumHQ/selenium/wiki/InternetExplorerDriver#required-configuration)

5. Execute the test cases
 ```script
pytest -vv --browser=<browser> --local --splunk-host=<web_url> --splunk-port=<mgmt_url> --splunk-user=<username> --splunk-password=<password>
 ```
- Debug UI tests with selenium inside docker-compose stack.
>prerequisite:
> 1. Setup all env variables mentioned above. As BROWSER variable pickup one "chrome_grid" or "firefox_grid". TEST_TYPE=ui etc.
> 2. Install [VNC Viewer](https://www.realvnc.com/en/connect/download/viewer/)
1. To select which test should be run we can use DEBUG_TEST variable and setup it to ingest -k parameter
```bash
export DEBUG_TEST="-k test_name_to_run"
```
2. Build images and execute the test
```bash
docker-compose -f docker-compose.yml build
docker-compose -f docker-compose.yml up
```
To watch the logs form docker container which run the test We can use command
```bash
docker logs -f containter_test_name [ eg. docker logs -f splunk-add-on-for-servicenow_test_1]
```
during the test execution when container with selenium standandalone hub is up and running We can connect to it using VNC Viewer.
```bash
localhost:6000  # chrome grid adress
localhost:6001 # firefox grid adress
```
Password is "secret"

- Modinput

Install [splunk-add-on-for-modinput-test](https://github.com/splunk/splunk-add-on-for-modinput-test/releases/latest/) addon in splunk and set all variables in environment mentioned at [test_credentials.env](test_credentials.env) file with appropriate values encoded with base64 or add variables in pytest command mentioned in conftest file.
```bash
pytest -vv --username=<splunk_username> --password=<splunk_password> --splunk-url=<splunk_url> --remote
```