import os
import pytest

from selenium import webdriver
from applitools.selenium import BatchInfo, ClassicRunner, Eyes, Target, VisualGridRunner
from webdriver_manager.chrome import ChromeDriverManager
from applitools.common.selenium import BrowserType
from applitools.common import DeviceName
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from time import sleep
from applitools.common import logger, StdoutLogger
from selenium.webdriver.common.keys import Keys


@pytest.fixture(scope="session")
def batch_info():
    """
    Use one BatchInfo for all tests inside module
    """
    return BatchInfo("SecKit_Geolocation")


@pytest.fixture(name="driver", scope="session")
def driver_setup(splunk_web_uri):
    """
    New browser instance per test and quite.
    """
    driver = webdriver.Chrome(ChromeDriverManager().install())

    driver.get(f"{splunk_web_uri}en-US/account/logout")
    driver.implicitly_wait(45)

    driver.find_element(By.ID, "username").send_keys("admin")
    driver.find_element(By.ID, "password").send_keys("Changed@11")
    driver.find_element(By.XPATH, "//input[@value='Sign In']").click()

    driver.maximize_window()
    yield driver
    # Close the browser.
    driver.quit()


@pytest.fixture(name="runner", scope="session")
def runner_setup():
    """
    One test runner for all tests. Print test results in the end of execution.
    """
    # runner = ClassicRunner()
    runner = VisualGridRunner(10)
    yield runner
    all_test_results = runner.get_all_test_results()
    print(all_test_results)


@pytest.fixture(name="eyes", scope="function")
def eyes_setup(runner, batch_info):
    """
    Basic Eyes setup. It'll abort test if wasn't closed properly.
    """
    eyes = Eyes(runner)
    #eyes.is_disabled = True
    # Initialize the eyes SDK and set your private API key.
    eyes.api_key = os.environ["APPLITOOLS_API_KEY"]
    eyes.configure.add_browser(1200, 754, BrowserType.CHROME)
    eyes.configure.add_browser(1200, 754, BrowserType.FIREFOX)
    eyes.configure.add_browser(1200, 754, BrowserType.SAFARI)
    #Add orientation and s
    #eyes.configure.add_device_emulation(DeviceName.iPhone_X)
    eyes.configure.batch = batch_info
    yield eyes
    # If the test was aborted before eyes.close was called, ends the test as aborted.
    # eyes.close(False)
    #eyes.abort_async()
    eyes.abort_if_not_closed()


# def test_navigate_app_sidebar(eyes, driver, splunk_web_uri):
@pytest.mark.nondestructive
def test_ui_navigate_app_sidebar(driver, eyes, splunk_web_uri):
    # Start the test and set the browser's viewport size to 800x600.
    eyes.open(driver, "SecKit_Geolocation", "App Nav by sidebar")
    driver.get(f"{splunk_web_uri}en-US/app/launcher/home")
    eyes.check("App Nav by sidebar start at launcher", Target.window().fully())

    driver.find_element(By.CSS_SELECTOR, ".app:nth-child(2) .app-name").click()
    element = driver.find_element(By.XPATH, "//div[2]/a/div[2]")
    actions = ActionChains(driver)
    actions.move_to_element(element).perform()
    driver.find_element(By.XPATH, "//div[2]/a/div[2]").click()

    eyes.check("App Nav by sidebar success", Target.window().fully())
    # eyes.close(False)

    eyes.close()


@pytest.mark.nondestructive
def test_ui_navigate_app_menu(driver, splunk_web_uri, eyes):
    # Start the test and set the browser's viewport size to 800x600.

    eyes.open(driver, "SecKit_Geolocation", "App Nav by menu")
    driver.get(f"{splunk_web_uri}en-US/app/search/search")
    eyes.check("App Nav by menu start at search", Target.window().fully())

    driver.find_element(By.XPATH, "//div/div/a/span").click()
    driver.find_element(
        By.XPATH, "//span[contains(.,'SecKit Geolocation with Maxmind')]"
    ).click()
    eyes.check("App Nav by menu success", Target.window().fully())
    # eyes.close(False)
    eyes.close()


def test_ui_navigate_setup_input(driver, splunk_web_uri, eyes):

    # logger.set_logger(StdoutLogger())
    eyes.open(driver, "SecKit_Geolocation", "App Setup")
    driver.get(f"{splunk_web_uri}en-US/app/SecKit_SA_geolocation/configuration")
    eyes.check("Configuration Load", Target.window().fully())

    # driver.set_window_size(1440, 877)
    driver.find_element(By.ID, "addAccountBtn").click()
    element = driver.find_element(By.ID, "addAccountBtn")
    actions = ActionChains(driver)
    actions.move_to_element(element).perform()
    eyes.check("Configuration Add Account", Target.window().fully())

    # element = driver.find_element(By.CSS_SELECTOR, "body")
    # actions = ActionChains(driver)
    # actions.move_to_element(element, 0, 0).perform()
    driver.find_element(By.ID, "account-name").click()
    driver.find_element(By.ID, "account-name").send_keys("main")
    driver.find_element(By.ID, "account-username").click()
    driver.find_element(By.ID, "account-username").send_keys("accountid")
    driver.find_element(By.ID, "account-password").click()
    driver.find_element(By.ID, "account-password").send_keys("licensekey")
    eyes.check("Configuration Add Account Filled", Target.window().fully())

    element = driver.find_element(By.CSS_SELECTOR, ".submit-dialog")
    actions = ActionChains(driver)
    actions.move_to_element(element).perform()
    driver.find_element(By.CSS_SELECTOR, ".submit-dialog").click()

    element = driver.find_element(By.LINK_TEXT, "Action")
    eyes.check("Configuration Account Created", Target.window().fully())

    # driver.find_elements_by_xpath(
    #     '//*[@id="account-tab"]/div/div/div[2]/table/tbody/tr/td[1]'
    # )

    driver.find_element(By.LINK_TEXT, "Inputs").click()
    eyes.check("Inputs Load", Target.window().fully())

    element = driver.find_element(By.ID, "addInputBtn")
    actions = ActionChains(driver)
    actions.move_to_element(element).perform()
    driver.find_element(By.ID, "addInputBtn").click()
    eyes.check("Inputs New", Target.window().fully())

    driver.find_element(By.ID, "geoipupdate-name").click()
    driver.find_element(By.ID, "geoipupdate-name").send_keys("maininput")
    driver.find_element(By.ID, "geoipupdate-interval").send_keys("1000")
    element = driver.find_element(By.ID, "select2-chosen-8")
    actions = ActionChains(driver)
    actions.move_to_element(element).perform()
    # element = driver.find_element(By.CSS_SELECTOR, "body")
    # actions = ActionChains(driver)
    # actions.move_to_element(element, 0, 0).perform()
    element = driver.find_element(By.ID, "select2-chosen-8")
    actions = ActionChains(driver)
    actions.move_to_element(element).click_and_hold().perform()
    element = driver.find_element(By.ID, "select2-drop-mask")
    actions = ActionChains(driver)
    actions.move_to_element(element).release().perform()
    driver.find_element(By.ID, "s2id_autogen8_search").send_keys("main")
    driver.find_element(By.ID, "s2id_autogen8_search").send_keys(Keys.ENTER)
    eyes.check("Inputs New Filled", Target.window().fully())

    driver.find_element(By.CSS_SELECTOR, ".submit-btn").click()
    element = driver.find_element(By.CSS_SELECTOR, ".submit-btn")
    actions = ActionChains(driver)
    actions.move_to_element(element).perform()
    driver.find_element(By.LINK_TEXT, "Action").click()
    eyes.check("Inputs Created", Target.window().fully())

    driver.find_element(By.LINK_TEXT, "Delete").click()
    eyes.check("Inputs Delete", Target.window().fully())

    driver.find_element(By.CSS_SELECTOR, ".submit-btn").click()
    element = driver.find_element(By.CSS_SELECTOR, ".submit-btn")
    actions = ActionChains(driver)
    actions.move_to_element(element).perform()
    sleep(5)
    eyes.check("Inputs Deleted", Target.window().fully())

    driver.find_element(By.LINK_TEXT, "Configuration").click()
    driver.find_element(By.CSS_SELECTOR, ".actions").click()
    driver.find_element(By.LINK_TEXT, "Action").click()
    element = driver.find_element(By.LINK_TEXT, "Action")
    actions = ActionChains(driver)
    actions.move_to_element(element).perform()
    element = driver.find_element(By.LINK_TEXT, "Delete")
    actions = ActionChains(driver)
    actions.move_to_element(element).perform()
    # element = driver.find_element(By.CSS_SELECTOR, "body")
    # actions = ActionChains(driver)
    # actions.move_to_element(element, 0, 0).perform()
    driver.find_element(By.LINK_TEXT, "Delete").click()
    # element = driver.find_element(By.CSS_SELECTOR, "body")
    # actions = ActionChains(driver)
    # actions.move_to_element(element, 0, 0).perform()
    eyes.check("Configuration Account Delete", Target.window().fully())

    driver.find_element(By.CSS_SELECTOR, ".submit-dialog").click()
    sleep(5)
    eyes.check("Configuration Account Deleted", Target.window().fully())
    eyes.close()
