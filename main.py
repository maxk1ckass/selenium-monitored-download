import os
import sys
import shutil
import time

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.events import EventFiringWebDriver, AbstractEventListener
from selenium.webdriver.common.by import By

from pathlib import Path


# URL of the test webpage which includes the button to download a text file
URL = "file://%s" % (os.path.join(os.path.dirname(__file__), "index.html"))

DOWNLOAD_TEMP_FOLDER = os.path.join(os.path.dirname(__file__), "downloads")


def is_download_finished(temp_folder):
    firefox_temp_file = sorted(Path(temp_folder).glob('*.part'))
    chrome_temp_file = sorted(Path(temp_folder).glob('*.crdownload'))
    downloaded_files = sorted(Path(temp_folder).glob('*.*'))
    if (len(firefox_temp_file) == 0) and \
       (len(chrome_temp_file) == 0) and \
       (len(downloaded_files) >= 1):
        return downloaded_files
    else:
        return False


def delete_folder(folder):
    try:
        shutil.rmtree(folder)
    except OSError as e:
        print("Failed to delete folder, error: %s - %s." %
              (e.filename, e.strerror))


def wait_for_and_read_the_latest_downloaded_file():
    downloaded_files = None

    while True:
        downloaded_files = is_download_finished(DOWNLOAD_TEMP_FOLDER)
        if(downloaded_files):
            break
        time.sleep(0.1)

    print("@@@@@@@@@@@@", downloaded_files)

    delete_folder(DOWNLOAD_TEMP_FOLDER)


def open_chrome():
    chrome_options = webdriver.ChromeOptions()
    prefs = {"download.default_directory": DOWNLOAD_TEMP_FOLDER}
    chrome_options.add_experimental_option("prefs", prefs)
    # chrome_options.add_experimental_option("detach", True)
    driver = webdriver.Chrome(options=chrome_options)
    return driver


def register_button_on_click_listener(driver):
    class MyListener(AbstractEventListener):
        def before_navigate_to(self, url, driver):
            print("Before navigate to %s" % url)

        def after_navigate_to(self, url, driver):
            print("After navigate to %s" % url)

        def after_click(self, element, driver):
            print("After click.")

    return EventFiringWebDriver(driver, MyListener())


# use global variable to prevent the selenium browser driver instance from garbage collected,
# which makes the program to quit early.
g_driver = None


def main():
    global g_driver

    g_driver = open_chrome()

    g_driver = register_button_on_click_listener(g_driver)

    g_driver.get(URL)

    # g_driver.close()


if __name__ == "__main__":
    main()
