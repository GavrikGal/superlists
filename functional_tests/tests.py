from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.keys import Keys
import time


MAX_WAIT = 3


class NewVisitorTest(LiveServerTestCase):
    """ Тест нового посетителя """

    def setUp(self):
        """установка"""
        self.browser = webdriver.Firefox()

    def tearDown(self) -> None:
        """демонтаж"""
        self.browser.quit()

    def wait_for_row_in_list_table(self, row_text):
        """ожидать строку в таблице списка"""
        start_time = time.time()
        while True:
            try:
                table = self.browser.find_element_by_id('id_list_table')
                rows = table.find_elements_by_tag_name('tr')
                self.assertIn(row_text, [row.text for row in rows])
                return
            except (AssertionError, WebDriverException) as e:
                if time.time()-start_time > MAX_WAIT:
                    raise e
                time.sleep(0.1)

    def test_can_start_a_list_and_retrieve_it_later(self):
        """тест: можно начать список и получить его позже"""

        # Эдит хочет оценить доступность домашней страницы
        self.browser.get(self.live_server_url)

        # Она видит, что заголовок и шапка страницы говорят о списках неотложных дел
        self.assertIn('To-Do', self.browser.title)
        header_test = self.browser.find_element_by_tag_name('h1').text
        self.assertIn('To-Do', header_test)

        # Ей сразу же предлагается ввести элемент списка
        inputbox = self.browser.find_element_by_id('id_new_item')
        self.assertEqual(
            inputbox.get_attribute('placeholder'),
            'Enter a to-do item'
        )

        # Она набирает в текстовом поле "Купить павлиньи перья"
        inputbox.send_keys('Купить павлиньи перья')

        # Когда она нажимает enter, страница обновляется, и теперь страница
        # содержит "1: Купить павлиньи перья" в качестве элемента списка
        inputbox.send_keys(Keys.ENTER)
        self.wait_for_row_in_list_table('1: Купить павлиньи перья')

        # Текстовое поле по-прежнему приглашает ее добавить еще один элемент.
        # Она вводит "Сделать мушку из павлиньих перьев"
        inputbox = self.browser.find_element_by_id('id_new_item')
        inputbox.send_keys('Сделать мушку из павлиньих перьев')
        inputbox.send_keys(Keys.ENTER)

        # Страница обновляется снова, и теперь показывает оба элемента ее списка
        self.wait_for_row_in_list_table('1: Купить павлиньи перья')
        self.wait_for_row_in_list_table('2: Сделать мушку из павлиньих перьев')

        # Эдит интересно, запомнит ли сайт ее список. Далее она видит, что
        # сайт сгенерировал для нее уникальный URL-адрес - об этом выводится небольшой текст с объяснениями.
        self.fail('Закончить тест!')

# Она посещает этот URL-адрес - ее список по-прежнему там.

# Довольная она ложится спать
# tag