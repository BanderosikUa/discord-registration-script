import string
import threading
import time
import os
import random

from typing import NamedTuple
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import WebDriverException


class User(NamedTuple):
    email: str
    username: str
    password: str


def main(driver: WebDriver, user: User):
    _register(driver, user)
    token = _check_captcha(driver)
    if token:
        print(f'Your access token is: {token}')
        _login(driver, token=token)


def _register(driver: WebDriver, user: User):
    url = "https://discord.com/register"
    driver.get(url=url)
    time.sleep(5)
    driver.find_element('xpath', "//input[@type='email']").send_keys(user.email)
    driver.find_element('xpath', "//input[@type='text']").send_keys(user.username)
    driver.find_element('xpath', "//input[@type='password']").send_keys(user.password)

    actions = ActionChains(driver)
    time.sleep(.5)

    driver.find_elements('class name', 'css-1hwfws3')[0].click()
    actions.send_keys(str(random.randint(1, 12)))
    actions.send_keys(Keys.ENTER)
    actions.send_keys(str(random.randint(1, 28)))
    actions.send_keys(Keys.ENTER)
    actions.send_keys(str(random.randint(1990, 2001)))
    actions.send_keys(Keys.ENTER)
    actions.send_keys(Keys.TAB)
    actions.send_keys(Keys.ENTER)
    actions.perform()
    time.sleep(5)


def _check_captcha(driver: WebDriver) -> str|None:
    lock = threading.Lock()
    while True:
        lock.acquire()
        checker = input("Have you solved the captcha and submit? [y/n] > ")
        lock.release()
        if checker == "y":
            token = driver.execute_script(
                "let popup; popup = window.open('', '', `width=1,height=1`); if(!popup || !popup.document || !popup.document.write)"
                " console.log('Please allow popups'); window.dispatchEvent(new Event('beforeunload'));"
                " token = popup.localStorage.token.slice(1, -1); popup.close(); return token")
            return token
        elif checker == "n":
            return


def _login(driver: WebDriver, token: str):
    url = "https://discord.com/login"
    driver.get(url=url)
    driver.execute_script(
        """function login(token) {
                setInterval(() => {
                  document.body.appendChild(document.createElement `iframe`).contentWindow.localStorage.token = `"${token}"`
                }, 50);
                setTimeout(() => {
                  location.reload();
                }, 2500);
              }
            token = arguments[0];
            login(token);
            """,
        token
    )
    while __is_browser_alive(driver):
        time.sleep(1)


def __is_browser_alive(driver: WebDriver):
   try:
      driver.current_url
      return True
   except:
      return False


if __name__ == "__main__":
    PATH_TO_DRIVER = Path.cwd() / 'operadriver'
    options = webdriver.ChromeOptions()
    options.add_argument('allow-elevated-browser')
    options.add_experimental_option('w3c', True)

    email = input('Enter your email:').strip()
    username = input('Enter your username:').strip()
    password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    user = User(email=email, username=username, password=password)

    os.chmod(PATH_TO_DRIVER, 0o755)
    driver = webdriver.Chrome(options=options, executable_path=PATH_TO_DRIVER)

    try:
        # _login(driver, token=token)
        main(driver=driver, user=user)
    except Exception as e:
        if e != WebDriverException:
            print(e)
    finally:
        try:
            driver.close()
        except Exception as e:
            if e != WebDriverException:
                print(e)
        finally:
            driver.quit()