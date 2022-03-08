# Generated by Selenium IDE
import pytest
import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


class TestDefaultSuite():
  def setup_method(self, method):
      """Setup test suite.
        """
      self.driver = webdriver.Firefox()
      self.vars = {}
      self.wait = 0.5

  def teardown_method(self, method):
      """Shut down current test.
        """
      self.driver.quit()

  def login(self, usermail):
      """Login on with usermail test account.
        
        Arguments:
            usermail {string} -- mail from test account.
        """
      self.driver.get("http://localhost:5000/")
      self.driver.set_window_size(1536, 824)
      self.driver.find_element(By.LINK_TEXT, "Login").click()
      self.driver.find_element(By.ID, "email").click()
      self.driver.find_element(By.ID, "email").send_keys(usermail)
      self.driver.find_element(By.ID, "password").send_keys("thisIsATest1!")
      self.driver.find_element(By.ID, "password").send_keys(Keys.ENTER)

  def logout(self):
      """Logout and check we have loged out.
        """
      self.driver.find_element(By.LINK_TEXT, "Logout").click()
      assert self.driver.find_element(By.LINK_TEXT, "Login").text == "Login"

  def test_loginLogout(self):
    """Test to correct login and logout in the page.

            Steps:
                1. Click Log in
                2. Complete user credentials
                3. Submit
                4. Click Log Out
                5. Wait to be sure the page is rendered correctly
                6. Close
        """
    self.driver.get("http://localhost:5000/")
    self.driver.find_element(By.ID, "content").click()
    self.driver.find_element(By.LINK_TEXT, "Log In").click()
    self.driver.find_element(By.ID, "email").click()
    self.driver.find_element(By.ID, "email").send_keys("p@p.es")
    self.driver.find_element(By.ID, "password").send_keys("!1Qwerty")
    self.driver.find_element(By.ID, "submit").click()
    self.driver.find_element(By.LINK_TEXT, "Log out").click()
    time.sleep(1)
    self.driver.close()
