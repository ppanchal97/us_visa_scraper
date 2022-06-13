# -*- coding: utf8 -*-

import requests, platform, time, json, random
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait as Wait
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from webdriver_manager.chrome import ChromeDriverManager

# Layers:
# 1. Selenium
# 2. ChromeDriver


USERNAME = 'parikspanchal@icloud.com'
PASSWORD = 'ApMrA9$7$tjaA6@F'
SCHEDULE = '40063233'

DATE_URL = "https://ais.usvisa-info.com/en-gb/niv/schedule/%s/appointment/days/16.json?appointments[expedite]=false" % SCHEDULE
TIME_URL = "https://ais.usvisa-info.com/en-gb/niv/schedule/%s/appointment/times/16.json?date=%%s&appointments[expedite]=false" % SCHEDULE
APPOINTMENT_URL = "https://ais.usvisa-info.com/en-gb/niv/schedule/%s/appointment" % SCHEDULE
HUB_ADDRESS = 'http://localhost:4444/wd/hub'
EXIT = False


options = Options()
options.headless = True


def get_drive():
    local_use = platform.system() == 'Darwin'
    if local_use:
        dr = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    else:
        dr = webdriver.Remote(command_executor=HUB_ADDRESS, desired_capabilities=DesiredCapabilities.CHROME)
    return dr


driver = get_drive()


def send(msg):
    url = "https://api.pushover.net/1/messages.json"
    data = {
        "token": "a3e35t15toqbaeuvms8fo2ktiforhb",
        "user": "u8jn5uzepg4d7nr164e4dkafn9zmjc",
        "message": msg
    }
    requests.post(url, data)
    print("sending push notification")


def push_notification(dates):
    msg = "date: "
    for d in dates:
        msg = msg + d.get('date') + '; '
    send(msg)


def login():
    # Bypass reCAPTCHA
    driver.get("https://ais.usvisa-info.com/en-gb/niv")
    time.sleep(1)
    a = driver.find_element(
        by=By.XPATH, value='//a[@class="down-arrow bounce"]')
    a.click()
    time.sleep(1)

    href = driver.find_element(by=By.XPATH,
                               value='//*[@id="header"]/nav/div[2]/div[1]/ul/li[3]/a')
    href.click()
    time.sleep(1)
    Wait(driver, 60).until(ec.presence_of_element_located((By.NAME, "commit")))

    a = driver.find_element(
        by=By.XPATH, value='//a[@class="down-arrow bounce"]')
    a.click()
    time.sleep(1)

    do_login_action()


def do_login_action():
    user = driver.find_element(by=By.ID, value='user_email')
    user.send_keys(USERNAME)
    time.sleep(random.randint(1, 3))

    pw = driver.find_element(by=By.ID, value='user_password')
    pw.send_keys(PASSWORD)
    time.sleep(random.randint(1, 3))

    box = driver.find_element(by=By.CLASS_NAME, value='icheckbox')
    box .click()
    time.sleep(random.randint(1, 3))

    btn = driver.find_element(by=By.NAME, value='commit')
    btn.click()
    time.sleep(random.randint(1, 3))

    Wait(driver, 60).until(ec.presence_of_element_located(
        (By.XPATH, "//a[contains(text(),'Continue')]")))
    print("Login Success! ")


def get_date():
    driver.get(DATE_URL)
    if not is_login():
        login()
        return get_date()
    else:
        content = driver.find_element(by=By.TAG_NAME, value='pre').text
        date = json.loads(content)
        return date


def get_time(date):
    time_url = TIME_URL % date
    driver.get(time_url)
    content = driver.find_element(by=By.TAG_NAME, value='pre').text
    data = json.loads(content)
    times = data.get("available_times")[-1]
    print("Get time successfully!")
    return times


def is_login():
    content = driver.page_source
    if content.find("error") != -1:
        return False
    return True


if __name__ == "__main__":
    print(datetime.now())
    login()
    dates = get_date()[:5]
    if len(dates) > 0:
        push_notification(dates[:5])
        print("statusCode: 200")
    else:
        print("No appointments available")
