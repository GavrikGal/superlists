from django.test import TestCase
from django.contrib import auth
from django.urls import reverse
from unittest.mock import patch, call

from accounts.models import Token
from accounts.models import User


class LogoutViewTest(TestCase):

    def test_redirect_to_home_page(self):
        """тест: переадресуется на домашнюю страницу"""
        response = self.client.get('/accounts/logout')
        self.assertRedirects(response, '/')

    def test_login_logout(self):
        """тест: вызов logout делает пользоватеся не авторизированным"""
        request = self.client.request().wsgi_request
        token = Token.objects.create(email='test.dmitry.gal@gamil.com')
        url = request.build_absolute_uri(
            reverse('login') + '?token=' + str(token.uid)
        )
        self.client.get(url)
        user = auth.get_user(self.client)
        self.assertTrue(user.is_authenticated)
        self.assertFalse(user.is_anonymous)
        self.client.get('/accounts/logout')
        user = auth.get_user(self.client)
        self.assertFalse(user.is_authenticated)


@patch('accounts.views.auth')
class LoginViewTest(TestCase):

    def test_redirects_to_home_page(self, mock_auth):
        """тест: переадресуется на домашнюю страницу"""
        response = self.client.get('/accounts/login?token=abcd123')
        self.assertRedirects(response, '/')

    def test_calls_authenticate_with_uid_from_get_request(self, mock_auth):
        """тест: вызывается authenticate с uid из GET-запроса"""
        self.client.get('/accounts/login?token=abcd123')
        self.assertEqual(
            mock_auth.authenticate.call_args,
            call(uid='abcd123')
        )

    def test_calls_auth_login_with_user_if_there_is_one(self, mock_auth):
        """тест: вызывается auth_login с пользователем, если такой имеется"""
        response = self.client.get('/accounts/login?token=abcd123')
        self.assertEqual(
            mock_auth.login.call_args,
            call(response.wsgi_request, mock_auth.authenticate.return_value)
        )

    def test_does_not_login_if_user_is_not_authenticated(self, mock_auth):
        """тест: не регисьрируется в системе, если пользователь НЕ аутентифицирован"""
        mock_auth.authenticate.return_value = None
        self.client.get('/accounts/login?token=abcd123')
        self.assertFalse(mock_auth.login.called, False)


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
