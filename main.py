import os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

# URL of the test webpage which includes the button to download a text file
URL = "file://%s" % (os.path.join(os.path.dirname(__file__), "index.html"))

driver = webdriver.Chrome()
driver.get(URL)

# driver.close()
