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

    driver.find_element(By.ID, "username").send_keys("admin")
    driver.find_element(By.ID, "password").send_keys("Changed@11")
    sleep(5)
    driver.find_element(By.XPATH, "//input[@value='Sign In']").click()

    driver.implicitly_wait(45)
    driver.maximize_window()
    yield driver
    # Close the browser.
    driver.quit()


@pytest.fixture(name="runner", scope="session")
def runner_setup():
    """
    One test runner for all tests. Print test results in the end of execution.
    """
    runner = ClassicRunner()
    #runner = VisualGridRunner()
    yield runner
    all_test_results = runner.get_all_test_results()
    print(all_test_results)


@pytest.fixture(name="eyes", scope="function")
def eyes_setup(runner, batch_info):
    """
    Basic Eyes setup. It'll abort test if wasn't closed properly.
    """
    eyes = Eyes(runner)
    # Initialize the eyes SDK and set your private API key.
    eyes.api_key = os.environ["APPLITOOLS_API_KEY"]
    eyes.configure.add_browser(800, 600, BrowserType.CHROME)
    eyes.configure.add_browser(700, 500, BrowserType.FIREFOX)
    eyes.configure.add_browser(1200, 800, BrowserType.SAFARI)
    eyes.configure.add_device_emulation(DeviceName.iPhone_X)
    eyes.configure.batch = batch_info
    yield eyes
    # If the test was aborted before eyes.close was called, ends the test as aborted.
    #eyes.close(False)
    #eyes.abort_if_not_closed()


# def test_navigate_app_sidebar(eyes, driver, splunk_web_uri):
@pytest.mark.nondestructive
def test_navigate_app_sidebar(driver, eyes, splunk_web_uri):
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
    #eyes.close(False)

    eyes.close()

@pytest.mark.nondestructive
def test_navigate_app_menu(driver, splunk_web_uri,eyes):
    # Start the test and set the browser's viewport size to 800x600.
    eyes.open(driver, "SecKit_Geolocation", "App Nav by menu")
    driver.get(f"{splunk_web_uri}en-US/app/search/search")
    eyes.check("App Nav by menu start at search", Target.window().fully())

    driver.find_element(By.XPATH, "//div/div/a/span").click()
    driver.find_element(
        By.XPATH, "//span[contains(.,'SecKit Geolocation with Maxmind')]"
    ).click()
    eyes.check("App Nav by menu success", Target.window().fully())
    #eyes.close(False)
    eyes.close()