import os
import shutil
import psutil
import time

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
#from selenium.webdriver.support.events import EventFiringWebDriver, AbstractEventListener
from selenium.webdriver.common.by import By

from pathlib import Path
import csv


# URL of the test webpage which includes the button to download a text file
URL = "file://%s" % (os.path.join(os.path.dirname(__file__), "index.html"))

DOWNLOAD_TEMP_FOLDER = os.path.join(os.path.dirname(__file__), "downloads")
RESULT_CSV_PATH = "result.csv"


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


def wait_for_and_read_the_latest_downloaded_file(driver):
    downloaded_files = None

    while True:
        # quit the loop if the browser windows is closed
        if not is_browser_open(driver):
            raise Exception('browser quitted.')

        downloaded_files = is_download_finished(DOWNLOAD_TEMP_FOLDER)
        if(downloaded_files):
            break

        time.sleep(0.1)

    recent_downloaded_file = str(downloaded_files[0])

    with open(recent_downloaded_file, 'r') as f:
        file_content = f.read()

    delete_folder(DOWNLOAD_TEMP_FOLDER)

    return file_content


def open_browser():
    chrome_options = webdriver.ChromeOptions()
    prefs = {"download.default_directory": DOWNLOAD_TEMP_FOLDER}
    chrome_options.add_experimental_option("prefs", prefs)
    # chrome_options.add_experimental_option("detach", True)
    driver = webdriver.Chrome(options=chrome_options)
    return driver


def is_browser_open(driver):
    try:
        driver_process = psutil.Process(driver.service.process.pid)
        browser_process = driver_process.children()
        if browser_process:
            browser_process = browser_process[0]
            return browser_process.is_running()
        return False
    except Exception as e:
        return False


def read_additional_info_from_webpage(driver):
    element = driver.find_element(By.CSS_SELECTOR, "#name")
    return element.text


def main():
    driver = open_browser()

    driver.get(URL)

    # check the downloaded files
    while True:
        try:
            # wait for the most recent file download and read the content
            content = wait_for_and_read_the_latest_downloaded_file(driver)

            # get some additional text from the webpage
            additional_info = read_additional_info_from_webpage(driver)

            print('Downloaded new file, content: "%s", additional info: "%s", now writing to %s.' % (
                content, additional_info, RESULT_CSV_PATH))

            # write the result into a csv
            with open(RESULT_CSV_PATH, 'a+', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow([content, additional_info])

        except Exception as e:
            print("App quitting, error message:", e)
            break

    # driver.close()


if __name__ == "__main__":
    main()
