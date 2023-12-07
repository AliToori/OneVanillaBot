#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    *******************************************************************************************
    OneVanillaBot: OneVanilla Captcha Solver Bot
    Author: Ali Toori, Python Developer
    Website: https://botflocks.com/
    *******************************************************************************************
"""
import csv
import json
import logging.config
import os
import pickle
import random
import re
import zipfile
import requests
import pyautogui
import time
from datetime import datetime, timedelta
from multiprocessing import freeze_support
from pathlib import Path
from time import sleep
import ntplib
import pandas as pd
import pyfiglet
import pytesseract
import urllib.request
from PIL import Image, ImageFont, ImageDraw
import base64
from io import BytesIO
from twocaptcha import TwoCaptcha
from selenium import webdriver
import undetected_chromedriver as uc
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class OneVanillaBot:
    def __init__(self):
        self.PROJECT_ROOT = Path(os.path.abspath(os.path.dirname(__file__)))
        self.file_settings = str(self.PROJECT_ROOT / 'BotRes/Settings.json')
        self.file_gift_cards = str(self.PROJECT_ROOT / 'BotRes/GiftCards.csv')
        self.directory_downloads = str(self.PROJECT_ROOT / 'BotRes/Downloads/')
        self.image_path = str(self.PROJECT_ROOT / 'BotRes/Downloads/image.png')
        self.fonts_path = str(self.PROJECT_ROOT / 'BotRes/Monaco.ttf')
        self.proxies = self.get_proxies()
        self.user_agents = self.get_user_agents()
        self.settings = self.get_settings()
        self.twocaptcha_api_key = self.settings["Settings"]["2CaptchaAPIKey"]
        self.twocaptcha_solver = TwoCaptcha(apiKey=self.twocaptcha_api_key)
        self.proxy = self.settings["Settings"]["ProxyServer"]
        self.onevanilla_url = 'https://onevanilla.com/#/'
        self.LOGGER = self.get_logger()
        self.logged_in = False
        self.driver = None

    @staticmethod
    def get_logger():
        """
        Get logger file handler
        :return: LOGGER
        """
        logging.config.dictConfig({
            "version": 1,
            "disable_existing_loggers": False,
            'formatters': {
                'colored': {
                    '()': 'colorlog.ColoredFormatter',  # colored output
                    # --> %(log_color)s is very important, that's what colors the line
                    'format': '[%(asctime)s,%(lineno)s] %(log_color)s[%(message)s]',
                    'log_colors': {
                        'DEBUG': 'green',
                        'INFO': 'cyan',
                        'WARNING': 'yellow',
                        'ERROR': 'red',
                        'CRITICAL': 'bold_red',
                    },
                },
                'simple': {
                    'format': '[%(asctime)s,%(lineno)s] [%(message)s]',
                },
            },
            "handlers": {
                "console": {
                    "class": "colorlog.StreamHandler",
                    "level": "INFO",
                    "formatter": "colored",
                    "stream": "ext://sys.stdout"
                },
                "file": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "level": "INFO",
                    "formatter": "simple",
                    "filename": "OneVanillaBot.log",
                    "maxBytes": 5 * 1024 * 1024,
                    "backupCount": 1
                },
            },
            "root": {"level": "INFO",
                     "handlers": ["console", "file"]
                     }
        })
        return logging.getLogger()

    @staticmethod
    def enable_cmd_colors():
        # Enables Windows New ANSI Support for Colored Printing on CMD
        from sys import platform
        if platform == "win32":
            import ctypes
            kernel32 = ctypes.windll.kernel32
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)

    @staticmethod
    def banner():
        pyfiglet.print_figlet(text='____________ OneVanillaBot\n', colors='RED')
        print('Author: AliToori, Full-Stack Python Developer\n'
              'Website: https://boteaz.com\n'
              '************************************************************************')

    def get_settings(self):
        """
        Creates default or loads existing settings file.
        :return: settings
        """
        if os.path.isfile(self.file_settings):
            with open(self.file_settings, 'r') as f:
                settings = json.load(f)
            return settings
        settings = {"Settings": {
            "Email": "email@gmail.com",
            "Password": "password",
        }}
        with open(self.file_settings, 'w') as f:
            json.dump(settings, f, indent=4)
        with open(self.file_settings, 'r') as f:
            settings = json.load(f)
        return settings

    # Loads proxies from local CSV file
    def get_proxies(self):
        file_proxies = str(self.PROJECT_ROOT / 'BotRes/Proxies.csv')
        proxy_list = pd.read_csv(self.file_proxies, index_col=None)
        proxies = []
        for proxy in proxy_list.iloc:
            if proxy["Password"] is not None:
                username = proxy["Username"]
                password = proxy["Password"]
                ip = proxy["IP"]
                port = proxy["Port"]
                proxy = f'http://{username}:{password}@{ip}:{port}'
                proxies.append(proxy)
            elif len(proxy_parts) == 2:
                ip = proxy["IP"]
                port = proxy["Port"]
                proxy = f'{ip}:{port}'
                proxies.append(proxy)
        return proxies

    # Get random user agent
    def get_user_agents(self):
        file_uagents = str(self.PROJECT_ROOT / 'BotRes/user_agents.txt')
        with open(file_uagents) as f:
            content = f.readlines()
        return [x.strip() for x in content]

    # Get proxy web driver
    def get_driver(self, proxy=False, proxies_from_file=False, headless=False):
        self.LOGGER.info(f'Launching browser')
        driver_bin = str(self.PROJECT_ROOT / "BotRes/bin/chromedriver.exe")
        service = Service(executable_path=driver_bin)
        options = webdriver.ChromeOptions()
        # options.add_argument("--start-maximized")
        # options.add_argument("--disable-extensions")
        # options.add_argument("--disable-notifications")
        # options.add_argument("--disable-blink-features")
        # options.add_argument("--disable-dev-shm-usage")
        # options.add_argument("--no-sandbox")
        # options.add_argument("--disable-gpu")
        # options.add_argument("--dns-prefetch-disable")
        # options.add_argument('--ignore-ssl-errors')
        # options.add_argument('--ignore-certificate-errors')
        # options.add_argument("--disable-blink-features=AutomationControlled")
        # options.add_experimental_option('excludeSwitches', ['enable-logging'])
        # options.add_experimental_option("excludeSwitches", ["enable-automation"])
        # options.add_experimental_option('useAutomationExtension', False)
        # prefs = {"directory_upgrade": True,
        #          "credentials_enable_service": False,
        #          "profile.password_manager_enabled": False,
        #          "profile.default_content_settings.popups": False,
        #          f"download.default_directory": f"{self.directory_downloads}",
        #          "profile.default_content_setting_values.geolocation": 2}
        # options.add_experimental_option("prefs", prefs)
        # options.add_argument(F'--user-agent={random.choice(self.user_agents)}')
        if proxy:
            # If using proxies from a list
            if proxies_from_file:
                options.add_argument(f"--proxy-server={random.choice(self.proxies)}")
            else:
                options.add_argument(f"--proxy-server={self.proxy}")
        if headless:
            options.add_argument('--headless')
        # driver = webdriver.Chrome(service=service, options=options)
        driver = uc.Chrome()
        return driver

    @staticmethod
    def wait_until_visible(driver, css_selector=None, element_id=None, name=None, class_name=None, tag_name=None, duration=10000, frequency=0.01):
        if css_selector:
            WebDriverWait(driver, duration, frequency).until(EC.visibility_of_element_located((By.CSS_SELECTOR, css_selector)))
        elif element_id:
            WebDriverWait(driver, duration, frequency).until(EC.visibility_of_element_located((By.ID, element_id)))
        elif name:
            WebDriverWait(driver, duration, frequency).until(EC.visibility_of_element_located((By.NAME, name)))
        elif class_name:
            WebDriverWait(driver, duration, frequency).until(EC.visibility_of_element_located((By.CLASS_NAME, class_name)))
        elif tag_name:
            WebDriverWait(driver, duration, frequency).until(EC.visibility_of_element_located((By.TAG_NAME, tag_name)))

    # Captcha solver for reCaptcha V2 and V3
    def solve_captcha(self):
        # self.clear_downloads_directory(self.directory_downloads)
        self.LOGGER.info(f'Solving captcha')
        captcha_page_url = "https://www.onevanilla.com/#/"
        site_key_v2 = "6Lc7IcIUAAAAAOPBNC4usz2kFYS23xU-zVjCYsSl"
        site_key_v3 = "6LfQZWwfAAAAANFYIqeDGZbDRkhdYuyhdulkr9uy"
        captcha_response = self.twocaptcha_solver.recaptcha(sitekey=site_key_v2, url=captcha_page_url)
        captcha_token = captcha_response["code"]
        self.LOGGER.info(f'Captcha token: {captcha_token}')
        self.LOGGER.info(f'Submitting captcha')
        # self.wait_until_visible(driver=self.driver, css_selector='[id="g-recaptcha-response"]')
        self.driver.execute_script(f'document.getElementById("g-recaptcha-response").innerHTML="{captcha_token}";')
        self.driver.execute_script(f"___grecaptcha_cfg.clients['0']['B']['B']['callback']('{captcha_token}');")
        self.LOGGER.info(f'Captcha submitted successfully')
        sleep(5000)
        self.save_screenshot(f"{self.directory_downloads}{datetime.now().strftime('%d-%m-%Y %H-%M-%S')}.png")
        try:
            self.wait_until_visible(driver=self.driver, css_selector='[class="alert alert-warn"]', duration=3)
            alert = self.driver.find_element(By.CSS_SELECTOR, '[class="alert alert-warn"]').text[:-2]
            sleep(5)
            if 'A system error has occurred' in alert:
                self.LOGGER.info(f'An Error occurred: {alert}')
        except:
            pass

    # Retrieves gift card data from the website
    def get_gift_card_balance(self, gift_card):
        card_number = str(gift_card["CardNumber"]).strip()
        card_expiry = str(gift_card["Expiry"]).strip()
        card_expiry_month = card_expiry.split('/')[0].strip()
        card_expiry_year = card_expiry.split('/')[1].strip()
        card_cvv = str(gift_card["CVV"])
        self.driver = self.get_driver(proxy=False)
        actions = ActionChains(driver=self.driver)
        # Fill card information
        self.driver.get("https://www.onevanilla.com/#/")
        self.LOGGER.info(f'Waiting for OneVanilla')
        self.wait_until_visible(driver=self.driver, css_selector='[id="cardnumber"]')
        self.driver.find_element(By.CSS_SELECTOR, '[id="cardnumber"]').send_keys(card_number)
        self.driver.find_element(By.CSS_SELECTOR, '[id="expMonth"]').send_keys(card_expiry_month)
        self.driver.find_element(By.CSS_SELECTOR, '[id="expirationYear"]').send_keys(card_expiry_year)
        self.driver.find_element(By.CSS_SELECTOR, '[id="cvv"]').send_keys(card_cvv)
        self.driver.find_element(By.CSS_SELECTOR, '[id="cvv"]').send_keys(Keys.ENTER)
        self.driver.find_element(By.CSS_SELECTOR, '[id="cvv"]').send_keys(Keys.ENTER)
        self.driver.find_element(By.CSS_SELECTOR, '[id="cvv"]').send_keys(Keys.ENTER)
        # Click Submit
        # self.wait_until_visible(driver=self.driver, css_selector='[id="brandLoginForm_button"]')
        # actions.move_to_element(self.driver.find_element(By.CSS_SELECTOR, '[id="brandLoginForm_button"]')).click().perform()
        # # self.driver.find_element(By.CSS_SELECTOR, '[id="brandLoginForm_button"]').click()
        self.LOGGER.info(f'SIGNIN BUTTON CLICKED')
        self.solve_captcha()
        # self.solve_captcha_audio()

    # returns file's path in the downloads folder/directory
    def get_file_path_download(self, directory_downloads):
        file_list = [str(self.PROJECT_ROOT / f'BotRes/Downloads/{f}') for f in os.listdir(directory_downloads) if os.path.isfile(str(self.PROJECT_ROOT / f'BotRes/Downloads/{f}'))]
        if len(file_list) == 1:
            file_download = file_list[0]
        else:
            file_download = file_list[-1]
        self.LOGGER.info(f'File has been retrieved : {file_download}')
        if os.path.isfile(file_download):
            return file_download
        else:
            self.LOGGER.info(f'Failed to download the file')

    # returns file's path in a the downloads folder/directory
    def clear_downloads_directory(self, directory_downloads):
        self.LOGGER.info(f'Checking Downloads Directory ...')
        # Check if Downloads Directory is there
        if os.path.isdir(directory_downloads):
            file_list = [str(self.PROJECT_ROOT / f'BotRes/Downloads/{f}') for f in os.listdir(directory_downloads) if
                         os.path.isfile(str(self.PROJECT_ROOT / f'BotRes/Downloads/{f}'))]
            if len(file_list) > 0:
                self.LOGGER.info(f'Clearing Downloads Directory ...')
                [os.remove(f) for f in file_list]
                self.LOGGER.info(f'Downloads Directory has been cleared')
            else:
                self.LOGGER.info(f'Downloads Directory is clear')
        else:
            self.LOGGER.info(f'Downloads Directory Not Found')

    # Removes file from the downloads directory
    def remove_file(self, file_download):
        if os.path.isfile(file_download):
            # Remove the file after extracting data from
            self.LOGGER.info(f'Removing temporary file: {file_download}')
            os.remove(file_download)
            self.LOGGER.info(f'Temporary file has been removed')
        else:
            self.LOGGER.info(f'Failed to remove the file')

    # Save website screenshot image
    def save_screenshot(self, image_path):
        self.LOGGER.info(f'Saving screenshot')
        self.driver.save_screenshot(image_path)
        # img_opened = Image.open(image_path)
        # to crop the captured image to size of that element
        # self.LOGGER.info(f'Cropping screenshot')
        # img_opened = img_opened.crop((int(50), int(50), int(980), int(380)))
        # img_opened.save(image_path, 'png')
        self.LOGGER.info(f'Screenshot saved: {image_path}')

    def main(self):
        freeze_support()
        self.enable_cmd_colors()
        # Print ASCII Art
        self.banner()
        self.LOGGER.info(f'OneVanillaBot launched')
        gift_cards = pd.read_csv(self.file_gift_cards, index_col=None)
        for i, gift_card in enumerate(gift_cards.iloc):
            self.LOGGER.info(f'Processing Card No. {i+1}: {gift_card["CardNumber"]}')
            self.get_gift_card_balance(gift_card=gift_card)


if __name__ == '__main__':
    OneVanillaBot().main()
