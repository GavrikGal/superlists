from django.test import TestCase
from unittest.mock import patch, call

from accounts.models import Token
import accounts.views


class SendLoginEmailViewTest(TestCase):
    """тест представления, которое отправляет сообщение для входа в систему"""

    def test_creates_token_associated_with_email(self):
        """тест: создается маркер, связанный с электронной почтой"""
        self.client.post('/accounts/send_login_email', data={
            'email': 'test.dmitry.gal@gmial.com'
        })
        token = Token.objects.first()
        self.assertEqual(token.email, 'test.dmitry.gal@gmial.com')

    @patch('accounts.views.send_mail')
    def test_sends_link_to_login_using_token_uid(self, mock_send_mail):
        """тест: отсылается ссылка на вход в систему, используя uid маркера"""
        self.client.post('/accounts/send_login_email', data={
            'email': 'test.dmitry.gal@gmial.com'
        })

        token = Token.objects.first()
        expected_url = f'http://testserver/accounts/login?token={token.uid}'
        (subject, body, from_email, to_list), kwargs = mock_send_mail.call_args
        self.assertIn(expected_url, body)

    @patch('accounts.views.messages')
    def test_adds_success_message_with_mocks(self, mock_messages):
        """тест: добавления сообщения об успехе"""
        response = self.client.post('/accounts/send_login_email', data={
            'email': 'test.dmitry.gal@gmial.com'
        })

        expected = "Проверте свою почту мы отправили вам ссылку, которую можно использовать для входа на сайт."
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
        # response = self.client.post('/accounts/send_login_email', data={
        #     'email': 'test.dmitry.gal@gmail.com'
        # })
        response = self.client.get('/accounts/login?token=abcd123')
        self.assertRedirects(response, '/')
