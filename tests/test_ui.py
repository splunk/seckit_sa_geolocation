import pytest
import pytest_html
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.chrome.options import Options


from time import sleep

# Fixture for Firefox
@pytest.fixture(params=["chrome", "firefox"], scope="class")
def driver_init(request, splunk_web_uri):
    if request.param == "chrome":
        web_driver = webdriver.Chrome()
    if request.param == "firefox":
        web_driver = webdriver.Firefox()
    request.cls.driver = web_driver

    web_driver.get(f"{splunk_web_uri}en-US/account/login")

    web_driver.find_element_by_css_selector("[name=username]").send_keys("admin")
    web_driver.find_element_by_css_selector("[name=password]").send_keys("Changed@11")

    web_driver.find_element_by_xpath("//input[@value='Sign In']").click()
    web_driver.implicitly_wait(30)

    yield
    web_driver.close()


@pytest.mark.usefixtures("driver_init")
class BasicTest:
    pass


class Test_URL(BasicTest):
    def test_navigate_app(self, splunk_web_uri, splunk_search_util):

        self.driver.get(f"{splunk_web_uri}en-US/app/launcher/home")

        self.driver.find_element(By.CSS_SELECTOR, ".app:nth-child(2) .app-name").click()
        element = self.driver.find_element(By.XPATH, "//div[2]/a/div[2]")
        actions = ActionChains(self.driver)
        actions.move_to_element(element).perform()
        self.driver.find_element(By.XPATH, "//div[2]/a/div[2]").click()

    def test_navigate_menu(self, splunk_web_uri, splunk_search_util):

        self.driver.get(f"{splunk_web_uri}en-US/app/search/search")

        self.driver.find_element(By.LINK_TEXT, "Search & Reporting").click()
        self.driver.find_element(
            By.XPATH, "//span[contains(.,'App: Search & Reporting')]"
        ).click()
        self.driver.find_element(By.XPATH, "//li[2]/a/span").click()
