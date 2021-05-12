import os
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.common.exceptions import WebDriverException, NoSuchElementException
from selenium.webdriver.firefox.options import Options
import time

MAX_WAIT = 3


class FunctionalTest(StaticLiveServerTestCase):
    """функциональный тест"""

    def setUp(self) -> None:
        """установка"""
        options = Options()
        # options.add_argument('--headless')
        # options.add_argument('--disable-gpu')
        self.browser = webdriver.Firefox(options=options)
        staging_server = os.environ.get('STAGING_SERVER')
        if staging_server:
            self.live_server_url = 'http://' + staging_server

    def tearDown(self) -> None:
        """демонтаж"""
        self.browser.quit()

    def get_item_input_box(self):
        """получить поле ввода для элемента"""
        return self.browser.find_element_by_id('id_text')

    def wait_for(self, fn):
        """ожидать"""
        start_time = time.time()
        while True:
            try:
                return fn()
            except (AssertionError, WebDriverException, NoSuchElementException) as e:
                if time.time() - start_time > MAX_WAIT:
                    raise e
                time.sleep(0.1)

    def wait_for_row_in_list_table(self, row_text):
        """ожидать строки в таблице списка"""
        start_time = time.time()
        while True:
            try:
                table = self.browser.find_element_by_id('id_list_table')
                rows = table.find_elements_by_tag_name('tr')
                self.assertIn(row_text, [row.text for row in rows])
                return
            except (AssertionError, WebDriverException) as e:
                if time.time() - start_time > MAX_WAIT:
                    raise e
                time.sleep(0.1)
