from selenium.webdriver.common.keys import Keys
from .base import wait


class ListPage(object):
    """страница списка"""

    def __init__(self, test):
        self.test = test

    def go_to_list_page(self):
        """перейти на страницу списка"""
        self.test.browser.get(self.test.live_server_url)
        self.test.wait_for(lambda: self.test.assertEqual(
            self.test.browser.find_element_by_tag_name('h1').text,
            'Start a new To-Do list'
        ))
        return self

    def get_table_rows(self):
        """получить строки таблицы"""
        return self.test.browser.find_elements_by_css_selector('#id_list_table tr')

    @wait
    def wait_for_row_in_list_table(self, item_text, item_number):
        row_text = '{}: {}'.format(item_number, item_text)
        rows = self.get_table_rows()
        self.test.assertIn(row_text, [row.text for row in rows])

    def get_item_input_box(self):
        """получить поле ввода для элемента"""
        return self.test.browser.find_element_by_id('id_text')

    def add_list_item(self, item_text):
        """добавить элемент списка"""
        new_item_no = len(self.get_table_rows()) + 1
        self.get_item_input_box().send_keys(item_text)
        self.get_item_input_box().send_keys(Keys.ENTER)
        self.wait_for_row_in_list_table(item_text, new_item_no)
        return self

    def get_share_box(self):
        """получить поле для обмена списками"""
        return self.test.browser.find_element_by_css_selector(
            'input[name="sharee"]'
        )

    def get_shared_with_list(self):
        """получить список от того, кто им делится"""
        return self.test.browser.find_elements_by_css_selector(
            '.list-sharee'
        )

    def share_list_with(self, email):
        """поделиться списком с"""
        self.get_share_box().send_keys(email)
        self.get_share_box().send_keys(Keys.ENTER)
        self.test.wait_for(lambda: self.test.assertIn(
            email,
            [item.text for item in self.get_shared_with_list()]
        ))

    def get_list_owner(self):
        """получить владельца списка"""
        return self.test.browser.find_element_by_id('id_list_owner').text
