#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import urllib
from random import randint, sample, choice
from time import sleep

import chromedriver_autoinstaller
import sentry_sdk
from anticaptchaofficial.recaptchav2enterpriseproxyless import *
from loguru import logger
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from selenium import webdriver
from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
    StaleElementReferenceException,
)
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

if not os.path.exists("cache"):
    os.mkdir("cache")

logger.add("debug.log", rotation="50 MB")
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# Download CRX
try:
    urllib.request.urlretrieve(
        "https://antcpt.com/downloads/anticaptcha/chrome/anticaptcha-plugin_v0.52.crx",
        "anticaptcha_latest.crx",
    )
except:
    pass

# Settings
LOGIN = os.environ.get("TIDAL_LOGIN", None)
PASSWORD = os.environ.get("TIDAL_PASSWORD", None)
ARTIST_URL = os.environ.get("ARTIST_URL", None)
IMPLICITLY_WAIT = int(os.environ.get("IMPLICITLY_WAIT"))
LOGIN_IMPLICITLY_WAIT = int(os.environ.get("LOGIN_IMPLICITLY_WAIT"))
ANTI_CAPTCHA_API = os.environ.get("ANTI_CAPTCHA_API", None)
SERVER_IP = requests.get("https://ipinfo.io/ip").content.decode("utf-8")
SERVER_PORT = os.environ.get("INSTANCE_PORT", None)
EXTERNAL_API_KEY = os.environ.get(
    "EXTERNAL_API_KEY", "7710cb1af53b5c22c218fd65952b3f64"
)
SENTRY_ADDRESS = os.environ.get("SENTRY", None)

sentry_sdk.init(SENTRY_ADDRESS, traces_sample_rate=1.0)

# Recaptcha Solver API
solver = recaptchaV2EnterpriseProxyless()
solver.set_verbose(1)
solver.set_key(ANTI_CAPTCHA_API)
solver.set_website_url("https://login.tidal.com/")
solver.set_website_key("6LcaN-0UAAAAAN056lYOwirUdIJ70tvy9QwNBajZ")

FAV_ARTISTS = [
    "Lady Gaga",
    "Ariana Grande",
    "Rihanna",
    "Madonna",
    "Ed Sheeran",
    "Billie Ellish",
    "Bruno Mars",
    "Dua Lipa",
    "Selena Gomez",
    "The Beatles",
    "Nirvana",
    "Radiohead",
    "Drake",
    "David Guetta",
    "deadmau5",
]
USER_AGENTS = (
    "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:45.0) Gecko/20100101 Firefox/45.0",
    "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 YaBrowser/20.9.3.136 Yowser/2.5 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36",
    "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.81 Safari/537.36 Maxthon/5.3.8.2000",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36",
)


class TidalPlayer:
    def __init__(
            self,
            email,
            password,
            artist_url,
            implicitly_wait,
            login_implicitly_wait=1,
            headless=False,
    ):

        self.chromedriver()

        self.email = email
        self.password = password
        self.artist_url = artist_url
        self.implicitly_wait = implicitly_wait
        self.login_implicitly_wait = login_implicitly_wait
        self.instance_login = LOGIN.split("@")[0]
        self.instance_name = self.instance_login + "_instance"
        self.server_ip = requests.get("https://ipinfo.io/ip").content.decode("utf-8")
        self.server_port = os.environ.get("INSTANCE_PORT")

        self.chrome_options = Options()

        self.chrome_options.add_extension("anticaptcha_latest.crx")

        self.options = (
            "--no-sandbox",
            "--disable-infobars",
            "--enable-precise-memory-info",
            "--disable-popup-blocking",
            "--disable-default-apps",
            "--window-size=1920,1080",
            "--enable-precise-memory-info",
            "--ignore-certificate-errors",
            "--test-type",
        )

        for option in self.options:
            self.chrome_options.add_argument(option)

        self.chrome_options.add_argument("--no-sandbox")

        if self.email is not None:
            self.chrome_options.add_argument(
                "--user-data-dir=cache/" + self.instance_login
            )
            pass
        else:
            raise KeyError("No LOGIN variable")

        if headless:
            self.chrome_options.add_argument("--headless")

        self.chrome_options.add_argument("--disable-dev-shm-usage")
        self.chrome_options.add_argument(
            '--user-agent="{0}"'.format(choice(USER_AGENTS))
        )
        self.driver = webdriver.Chrome(options=self.chrome_options)

    @staticmethod
    def chromedriver():
        chrome_version = chromedriver_autoinstaller.get_chrome_version()
        logger.debug("Google Chrome version {0} is installed.".format(chrome_version))
        try:
            logger.debug("Checking and/or installing chromedriver")
            chromedriver_autoinstaller.install()
        finally:
            logger.debug("Chromedriver is ok.")

    def acp_api_send_request(self, message_type, data: dict):
        message = {"receiver": "antiCaptchaPlugin", "type": message_type, **data}
        return self.driver.execute_script(
            """
        return window.postMessage({});
        """.format(
                json.dumps(message)
            )
        )

    def login(self):
        def fill_form():
            """Fill out the form and submit"""
            logger.debug("Started to filling out the form")
            login_field = self.driver.find_element_by_css_selector(
                "input[class*='client-input'][name='email']"
            )
            login_field.clear()
            login_field.send_keys(self.email)

            self.acp_api_send_request(
                "setOptions",
                {
                    "options": {
                        "antiCaptchaApiKey": "c1d44f165be66c2f63dc28a6608f67b6",
                    }
                },
            )

            WebDriverWait(self.driver, 120).until(
                lambda x: x.find_element_by_css_selector(".antigate_solver.solved")
            )

            next_step = self.driver.find_element_by_id("recap-invisible")
            next_step.click()

            self.driver.implicitly_wait(5)

            # if EC.frame_to_be_available_and_switch_to_it(0):
            #
            #     try:
            #         self.driver.find_element_by_xpath('//*[@id="password"]').click()
            #         logger.debug("Carried over, the captcha window did not appear")
            #     except NoSuchElementException:
            #         logger.warning("A window with captcha appeared")
            #         logger.warning("Solving captcha in process")
            #
            #         # g_response = solver.solve_and_return_solution()
            #         g_response = 1
            #
            #         logger.warning("Received the response from solver")
            #         if g_response != 0:
            #             self.driver.execute_script(
            #                 'document.getElementById("g-recaptcha-response").innerHTML = "%s"'
            #                 % g_response
            #             )
            #             # window = self.driver.find_element_by_xpath(
            #             #     '//iframe[contains(@title, "recaptcha")]'
            #             # )
            #             # window.send_keys(Keys.ESCAPE)
            #
            #             self.driver.implicitly_wait(5)
            #             next_step = self.driver.find_element_by_id("recap-invisible")
            #             next_step.click()
            #
            #             try:
            #                 logger.warning(
            #                     "Waiting 320 while captcha is solving manually."
            #                 )
            #                 WebDriverWait(self.driver, 920).until(
            #                     EC.presence_of_element_located(
            #                         (
            #                             By.XPATH,
            #                             '//*[@id="password"]',
            #                         )
            #                     )
            #                 )
            #             except (NoSuchElementException, StaleElementReferenceException):
            #                 logger.error("An error while solving captcha appeared.")
            #                 raise Exception("An error while solving captcha appeared.")
            #         else:
            #             if EC.visibility_of_element_located(
            #                     (
            #                             By.CSS_SELECTOR,
            #                             "input[class*='client-input'][name='email']",
            #                     )
            #             ) and EC.visibility_of_element_located(
            #                 (
            #                         By.XPATH,
            #                         '//*[@id="password"]',
            #                 )
            #             ):
            #                 logger.success("Captcha solved successfully")
            #             else:
            #                 raise Exception("Login Error while trying to solve captcha")

            WebDriverWait(self.driver, 250).until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        '//*[@id="password"]',
                    )
                )
            )

            if EC.visibility_of_element_located(
                    (
                            By.CSS_SELECTOR,
                            "input[class*='client-input'][name='email']",
                    )
            ) and EC.visibility_of_element_located(
                (
                        By.XPATH,
                        '//*[@id="password"]',
                )
            ):
                logger.success("Captcha solved successfully")
            else:
                raise Exception("Login Error while trying to solve captcha")

            self.driver.implicitly_wait(5)

            logger.success("Trying to fill out password.")
            sleep(5)
            password_field = self.driver.find_element_by_xpath('//*[@id="password"]')
            password_field.send_keys(self.password)
            # login_button = self.driver.find_element_by_xpath(
            #     '//*[@id="main-content"]/div/div[1]/div/div[2]/div/form/button'
            # )
            # login_button = self.driver.find_element_by_xpath('//div[contains(text(), " Log in ")]')
            # login_button.click()
            self.driver.find_element_by_xpath(
                '//*[@id="main-content"]/div/div[1]/div/div[2]/div/form'
            ).submit()

            if EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "div[class^='artistPickerContainer']")
            ):
                self.select_startup_artists()
            else:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located(
                        (
                            By.XPATH,
                            '//*[@id="main"]',
                        )
                    )
                )

        def assert_home():
            if "Home" in self.driver.title:
                logger.info("Successful confirmation of the player's home page")
                return True
            else:
                return

        self.driver.get("https://listen.tidal.com/login")

        while True:
            try:
                WebDriverWait(self.driver, self.login_implicitly_wait).until(
                    EC.presence_of_element_located(
                        (
                            By.XPATH,
                            '//*[@id="email"]',
                        )
                    )
                )
                logger.debug("Standard email / password login page found")
                fill_form()

            except (NoSuchElementException, TimeoutException):
                raise

            try:
                WebDriverWait(self.driver, self.login_implicitly_wait).until(
                    EC.presence_of_element_located(
                        (
                            By.XPATH,
                            '//div[contains(text(), "No, switch account")]',
                        )
                    )
                )
                logger.debug("Found a login form with confirmation")
                continue_button = self.driver.find_element_by_xpath(
                    '//div[contains(text(), "No, switch account")]'
                )
                continue_button.click()
                fill_form()
            except (NoSuchElementException, TimeoutException):
                raise

            if assert_home():
                break
            if EC.presence_of_element_located(
                    (
                            By.CSS_SELECTOR,
                            "div[class^='artistPickerWrapper']",
                    )
            ):
                self.select_startup_artists()
                break

    def select_startup_artists(self):
        try:
            if EC.presence_of_element_located(
                    (
                            By.CSS_SELECTOR,
                            "div[class^='artistPickerWrapper']",
                    )
            ):
                artists = self.driver.find_elements_by_css_selector(
                    "div[class^='artistWrapper']"
                )
                for artist in sample(
                        self.driver.find_elements_by_css_selector(
                            "div[class^='artistWrapper']"
                        ),
                        5,
                ):
                    artist.click()
                    self.driver.implicitly_wait(self.login_implicitly_wait)
                    sleep(1)

                WebDriverWait(self.driver, 250).until(
                    EC.element_to_be_clickable(
                        (
                            By.XPATH,
                            '//button[contains(text(), "Continue")]',
                        )
                    )
                )
                sleep(2)

                continue_button = self.driver.find_element_by_xpath(
                    '//button[contains(text(), "Continue")]'
                )
                continue_button.click()
                logger.debug(
                    "Artist has been successfully selected in the first run window"
                )
        except (NoSuchElementException, WebDriverException, ValueError):
            pass

    def get_album_page(self):
        try:
            logger.debug("Trying to go to the playback landing page")
            self.driver.get(self.artist_url)
            WebDriverWait(self.driver, self.implicitly_wait).until(
                EC.presence_of_element_located(
                    (
                        By.CSS_SELECTOR,
                        "div[data-test*='header-controls']",
                    )
                )
            )
            shuffle_button = self.driver.find_element_by_css_selector(
                "button[data-test*='shuffle-all']"
            )
            shuffle_button.click()

            WebDriverWait(self.driver, self.implicitly_wait).until(
                EC.presence_of_element_located(
                    (
                        By.CSS_SELECTOR,
                        "div[id*='footerPlayer']",
                    )
                )
            )

            WebDriverWait(self.driver, self.implicitly_wait).until(
                EC.presence_of_element_located(
                    (
                        By.CSS_SELECTOR,
                        "button[data-test*='pause']",
                    )
                )
            )
        except (NoSuchElementException, WebDriverException):
            logger.error(
                "An error occurred while navigating to the landing page and starting playback"
            )

    def set_cycle(self):
        repeat_button = self.driver.find_element_by_css_selector(
            "button[aria-label*='Repeat']"
        )
        if repeat_button.get_attribute("data-type") != "button__repeatAll":
            logger.debug("Loop playback setting")
            while repeat_button.get_attribute("data-type") != "button__repeatAll":
                repeat_button.click()
                sleep(0.1)

    def set_quality(self):
        quality_button = self.driver.find_element_by_css_selector(
            "button[title*='Settings'][type='button']"
        )
        if quality_button.get_attribute("data-test-streaming-quality") != "LOW":
            try:
                logger.debug("Setting the minimum playback quality")
                quality_button.click()
                WebDriverWait(self.driver, self.implicitly_wait).until(
                    EC.presence_of_element_located(
                        (
                            By.XPATH,
                            '//div[contains(text(), "Normal")]',
                        )
                    )
                )
                normal_quality = self.driver.find_element_by_xpath(
                    '//div[contains(text(), "Normal")]'
                )
                normal_quality.click()
            except (NoSuchElementException, WebDriverException):
                logger.error("An error occurred while trying to set minimum quality")

    def click_next_track(self):
        try:
            next_button = self.driver.find_element_by_css_selector(
                "button[data-type*='button__skip-next']"
            )
            next_button.click()
        except (WebDriverException, NoSuchElementException, TimeoutException):
            logger.error("An error occurred while trying to switch tracks.")
            pass

    def playing(self):
        while True:
            try:
                sleep(1)
                now_playing_track = self.driver.find_element_by_css_selector(
                    "div[data-test*='footer-track-title']"
                ).text
                now_playing_artist = self.driver.find_element_by_css_selector(
                    "a[data-test*='grid-item-detail-text-title-artist']"
                ).text
                current_time = self.driver.find_element_by_css_selector(
                    "time[data-test*='current-time']"
                ).text
                duration_time = self.driver.find_elements_by_css_selector(
                    "time[class*='duration-time']"
                )[1].text

                logger.debug(
                    "[{0}] | Now playing: {1} by {2} | [{3}]".format(
                        datetime.now().strftime("%d/%m/%y %H:%M:%S"),
                        now_playing_track,
                        now_playing_artist,
                        duration_time,
                    )
                )

                start_time = time.time()

                while int(current_time.replace(":", "")) < int(
                        duration_time.replace(":", "")
                ) - randint(10, 20):
                    current_time = self.driver.find_element_by_css_selector(
                        "time[data-test*='current-time']"
                    ).text

                    duration_time = self.driver.find_elements_by_css_selector(
                        "time[data-test*='duration-time']"
                    )[1].text

                    timer = time.time()
                    if float(round(timer - start_time)) > round(
                            float(duration_time.replace(":", ".")) * 60 + 30
                    ):
                        logger.warning(
                            "The timer caught a freeze, forced switching of the track."
                        )
                        next_button = self.driver.find_element_by_css_selector(
                            "button[data-type*='button__skip-next']"
                        )

                        try:
                            WebDriverWait(
                                self.driver, self.login_implicitly_wait
                            ).until(EC.element_to_be_clickable(next_button))
                        except:
                            pass
                        finally:
                            next_button.click()
                            self.driver.implicitly_wait(self.implicitly_wait)
                            if (
                                    now_playing_track
                                    != self.driver.find_element_by_css_selector(
                                "div[data-test*='footer-track-title']"
                            ).text
                            ):
                                logger.error("Lag. Try to reload playing")
                                break

                        logger.debug("Successful track switch")
                        break

                    continue

                try:
                    WebDriverWait(self.driver, self.login_implicitly_wait).until(
                        EC.element_to_be_clickable(
                            (
                                By.CSS_SELECTOR,
                                "button[data-type*='button__skip-next']",
                            )
                        )
                    )
                    next_button = self.driver.find_element_by_css_selector(
                        "button[data-type*='button__skip-next']"
                    )
                    next_button.click()
                except (
                        StaleElementReferenceException,
                        NoSuchElementException,
                        TimeoutException,
                ):
                    self.driver.quit()
                    break

                if (
                        now_playing_track
                        != self.driver.find_element_by_css_selector(
                    "div[data-test*='footer-track-title']"
                ).text
                ):
                    sleep(1)
                    continue
                else:
                    break

            except KeyboardInterrupt:
                break

    def run(self):
        if __name__ == "__main__":
            try:
                logger.success("The script is running now. Let's get started!")
                self.login()
                self.get_album_page()
                self.set_quality()
                self.set_cycle()

                while True:
                    self.playing()
            except Exception as exception:
                logger.error("Exception raised" + str(exception))
                logger.warning("Trying to restart process after wait 30 sec...")
                sleep(30)
                self.run()


tidal = TidalPlayer(LOGIN, PASSWORD, ARTIST_URL, IMPLICITLY_WAIT)

tidal.run()
