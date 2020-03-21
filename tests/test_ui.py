import os
import pytest

from selenium import webdriver
from applitools.selenium import Eyes, Target, BatchInfo, ClassicRunner
from webdriver_manager.chrome import ChromeDriverManager
from applitools.common.selenium import BrowserType
from applitools.common import DeviceName


@pytest.fixture(scope="module")
def batch_info():
    """
    Use one BatchInfo for all tests inside module
    """
    return BatchInfo("Some general Test cases name")


@pytest.fixture(name="driver", scope="function")
def driver_setup():
    """
    New browser instance per test and quite.
    """
    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.implicitly_wait(45)

    
    yield driver
    # Close the browser.
    driver.quit()


@pytest.fixture(name="runner", scope="module")
def runner_setup():
    """
    One test runner for all tests. Print test results in the end of execution.
    """
    runner = ClassicRunner()
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
    eyes.close(False)
    eyes.abort_if_not_closed()


def test_web_accessible(eyes, driver, splunk_web_uri):
    # Start the test and set the browser's viewport size to 800x600.
    eyes.open(driver, "SecKit_Geolocation", "Web Accessible")
    # Navigate the browser to the "hello world!" web-site.
    driver.get(f"{splunk_web_uri}en-US/account/login")
    driver.implicitly_wait(45)
    # Visual checkpoint #1.
    eyes.check("Login Window test", Target.window().fully())

    # End the test.
    # eyes.close(False)


def test_web_login_success(eyes, driver, splunk_web_uri):
    # Start the test and set the browser's viewport size to 800x600.
    eyes.open(driver, "SecKit_Geolocation", "Web Login")
    # Navigate the browser to the "hello world!" web-site.
    driver.get(f"{splunk_web_uri}en-US/account/login")
    eyes.check("Login Window", Target.window().fully())

    driver.find_element_by_css_selector("[name=username]").send_keys("admin")
    driver.find_element_by_css_selector("[name=password]").send_keys("Changed@11")
    driver.find_element_by_css_selector("[name=password]").send_keys("${KEY_ENTER}")
    eyes.check("Login Success", Target.window().fully())

    # End the test.


# eyes.close(False)
# def test_navigate_app(self, splunk_web_uri, splunk_search_util):

#     self.driver.get(f"{splunk_web_uri}en-US/app/launcher/home")

#     self.driver.find_element(By.CSS_SELECTOR, ".app:nth-child(2) .app-name").click()
#     element = self.driver.find_element(By.XPATH, "//div[2]/a/div[2]")
#     actions = ActionChains(self.driver)
#     actions.move_to_element(element).perform()
#     self.driver.find_element(By.XPATH, "//div[2]/a/div[2]").click()

#     self.eyes.check("Step - Nav via sidebar", Target.window().fully())

# def test_navigate_menu(self, splunk_web_uri, splunk_search_util):

#     self.driver.get(f"{splunk_web_uri}en-US/app/search/search")

#     self.eyes.check("Step - Check Search App", Target.window().fully())
#     self.driver.find_element(By.LINK_TEXT, "Search & Reporting").click()
#     self.driver.find_element(
#         By.XPATH, "//span[contains(.,'App: Search & Reporting')]"
#     ).click()
#     self.driver.find_element(By.XPATH, "//li[2]/a/span").click()

#     self.eyes.check("Step - Nav via Menu", Target.window().fully())

