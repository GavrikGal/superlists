from django.test import TestCase
from unittest.mock import patch, call

import accounts.views


class SendLoginEmailViewTest(TestCase):
    """тест представления, которое отправляет сообщение для входа в систему"""

    @patch('accounts.views.messages')
    def test_adds_success_message_with_mocks(self, mock_messages):
        """тест: добавления сообщения об успехе"""
        response = self.client.post('/accounts/send_login_email', data={
            'email': 'test.dmitry.gal@gmial.com'
        })

        expected = "Проверте совю почту мы отправили вам ссылку, которую можно использовать для входа на сайт."
        self.assertEqual(
            mock_messages.success.call_args,
            call(response.wsgi_request, expected),
        )

    @patch('accounts.views.send_mail')
    def test_sends_mail_to_address_from_post(self, mock_send_mail):
        """тест: отправляется сообщение на адрес из метода post"""
        self.client.post('/accounts/send_login_email', data={
            'email': 'test.dmitry.gal@gmail.com'
        })
        self.assertTrue(mock_send_mail.called, True)
        (subject, body, from_email, to_list), kwargs = mock_send_mail.call_args
        self.assertEqual(subject, 'Your login link for Superlists')
        self.assertEqual(from_email, 'noreply@superlists')
        self.assertEqual(to_list, ['test.dmitry.gal@gmail.com'])

    def test_redirects_to_home_page(self):
        """тест: переадресуется на домашнюю страницу"""
        response = self.client.post('/accounts/send_login_email', data={
            'email': 'test.dmitry.gal@gmail.com'
        })
        self.assertRedirects(response, '/')
