from django.contrib.auth import get_user_model
from django.http import HttpRequest
from django.test import TestCase
from django.utils.html import escape
from unittest.mock import patch, Mock
import unittest


from lists.models import Item, List
from lists.forms import (
    DUPLICATE_ITEM_ERROR, EMPTY_ITEM_ERROR,
    ExistingListItemForm, ItemForm
)
from lists.views import new_list


User = get_user_model()


class ShareListUnitTest(unittest.TestCase):
    """модульный тест для возможности делиться списком"""
    pass


class ShareListIntegratedTest(TestCase):
    """интегрированный тест для возможности делиться списком"""

    def test_post_redirects_lo_lists_page(self):
        """тест переадресации в представление списка"""
        other_list = List.objects.create()
        correct_list = List.objects.create()
        user = User.objects.create(email='a@b.com')
        response = self.client.post(f'/lists/{correct_list.id}/share/', data={'sharee': user.email})
        self.assertRedirects(response, f'/lists/{correct_list.id}/')

    def test_post_with_new_email_passed(self):
        """тест: post-запрос с email, которого нет в БД не поднимает исключение"""
        self.fail('сделать')

    def test_post_with_email_add_user_to_shared_with(self):
        """тест: post-запрос с email добавляет пользователя с указаным email в
           атрибут списка shared_with"""
        user = User.objects.create(email='a@b.com')
        list_ = List.objects.create()
        self.client.post(f'/lists/{list_.id}/share/', data={'sharee': user.email})
        self.assertIn(user, list_.shared_with.all())


@patch('lists.views.NewListForm')
@patch('lists.views.redirect')
class NewListViewUnitTest(unittest.TestCase):
    """модульный тест нового представления списка"""

    def setUp(self):
        """установка"""
        self.request = HttpRequest()
        self.request.POST['text'] = 'new list item'
        self.request.user = Mock()

    def test_passes_POST_data_to_NewListForm(self, mock_redirect, mockNewListForm):
        """тест: передаются POST-данные в новую форму списка"""
        new_list(self.request)
        mockNewListForm.assert_called_once_with(data=self.request.POST)

    def test_saves_form_with_owner_if_form_valid(self, mock_redirect, mockNewListForm):
        """тест: сохраняет форму с владельцем, если форма допустима"""
        mock_form = mockNewListForm.return_value
        mock_form.is_valid.return_value = True
        new_list(self.request)
        mock_form.save.assert_called_once_with(owner=self.request.user)

    def test_redirects_to_form_returned_object_if_form_valid(
            self, mock_redirect, mockNewListForm
    ):
        """тест: переадресует в возвращаемый формой объект,
           если форма допустима"""
        mock_form = mockNewListForm.return_value
        mock_form.is_valid.return_value = True

        response = new_list(self.request)

        self.assertEqual(response, mock_redirect.return_value)
        mock_redirect.assert_called_once_with(mock_form.save.return_value)

    @patch('lists.views.render')
    def test_render_home_template_with_form_if_form_invalid(
            self, mock_render, mock_redirect, mockNewListForm
    ):
        """тест: отображает домашний шаблон с формой, если форма недопустима"""
        mock_form = mockNewListForm.return_value
        mock_form.is_valid.return_value = False
        response = new_list(self.request)

        self.assertEqual(response, mock_render.return_value)

        mock_render.assert_called_once_with(
            self.request, 'lists/home.html', {'form': mock_form}
        )

    def test_does_not_save_if_form_invalid(self, mock_redirect, mockNewListForm):
        """тест: не сохраняет, если форма недопустима"""
        mock_form = mockNewListForm.return_value
        mock_form.is_valid.return_value = False
        new_list(self.request)
        self.assertFalse(mock_form.save.called)


class NewListViewIntegratedTest(TestCase):
    """интергрированный тест нового представления списка"""
    #
    # def test_for_invalid_input_renders_home_template(self):
    #     """тест на недопустимый ввод: отображает домашний шаблон"""
    #     response = self.client.post('/lists/new', data={'text': ''})
    #     self.assertEqual(response.status_code, 200)
    #     self.assertTemplateUsed(response, 'lists/home.html')

    def test_for_invalid_input_doesnt_save_but_shows_errors(self):  # оставить
        """тест: ошибки валидации выводятся на домашней странице"""
        response = self.client.post('/lists/new', data={'text': ''})
        self.assertEqual(List.objects.count(), 0)
        self.assertContains(response, escape(EMPTY_ITEM_ERROR))

    # def test_for_invalid_input_passes_form_to_template(self):
    #     """тест на недопустимый ввод: форма передается в шаблон"""
    #     response = self.client.post('/lists/new', data={'text': ''})
    #     self.assertIsInstance(response.context['form'], ItemForm)
    #
    # def test_invalid_list_items_arent_saved(self):
    #     """тест: не сохраняются недопустимые элементы списка"""
    #     self.client.post('/list/new', data={'text': ''})
    #     self.assertEqual(List.objects.count(), 0)
    #     self.assertEqual(Item.objects.count(), 0)

    def test_can_save_a_POST_request(self):  # оставить
        """тест: можно сохранить post-запрос"""
        self.client.post('/lists/new', data={'text': 'A new list item'})
        self.assertEqual(Item.objects.count(), 1)
        new_item = Item.objects.first()
        self.assertEqual(new_item.text, 'A new list item')

    # def test_redirects_after_POST(self):
    #     """тест: переадресует после post-запроса"""
    #     response = self.client.post('/lists/new', data={'text': 'A new list item'})
    #     new_list = List.objects.first()
    #     self.assertRedirects(response, f'/lists/{new_list.id}/')

    def test_list_owner_is_saved_if_user_is_authenticated(self):  # оставить
        """тест: владелец сохраняется, если
           пользователь аутентифицирован"""
        user = User.objects.create(email='a@b.com')
        self.client.force_login(user)
        self.client.post('/lists/new', data={'text': 'new item'})
        list_ = List.objects.first()
        self.assertEqual(list_.owner, user)


class MyListsTest(TestCase):
    """тест 'Моих списков'"""

    def test_my_lists_url_renders_my_lists_template(self):
        """тест: url-адрес для 'моих списков' отображается"""
        User.objects.create(email='a@b.com')
        response = self.client.get('/lists/users/a@b.com/')
        self.assertTemplateUsed(response, 'lists/my_lists.html')

    def test_passes_correct_owner_to_template(self):
        """тест: передается правильный владелец в шаблон"""
        User.objects.create(email='wrong@owner.com')
        correct_user = User.objects.create(email='a@b.com')
        response = self.client.get('/lists/users/a@b.com/')
        self.assertEqual(response.context['owner'], correct_user)


class ListViewTest(TestCase):
    """Тест представления списка"""

    def post_invalid_input(self):
        """отправляет недопустимый ввод"""
        list_ = List.objects.create()
        return self.client.post(
            f'/lists/{list_.id}/',
            data={'text': ''}
        )

    def test_duplicate_item_validation_errors_end_up_on_lists_page(self):
        """тест: ошибки валидации повторяющегося элемента оканчиваются
           на стнанице списков"""
        list1 = List.objects.create()
        item1 = Item.objects.create(list=list1, text='textey')
        response = self.client.post(
            f'/lists/{list1.id}/',
            data={'text': 'textey'}
        )

        expected_error = escape(DUPLICATE_ITEM_ERROR)
        self.assertContains(response, expected_error)
        self.assertTemplateUsed(response, 'lists/list.html')
        self.assertEqual(Item.objects.all().count(), 1)

    def test_displays_item_form(self):
        """тест отображения формы для элемента"""
        list_ = List.objects.create()
        response = self.client.get(f'/lists/{list_.id}/')
        self.assertIsInstance(response.context['form'], ExistingListItemForm)
        self.assertContains(response, 'name="text"')

    def test_for_invalid_input_nothing_saved_to_db(self):
        """тест на недопустимый ввод: ничего не сохраняется в БД"""
        self.post_invalid_input()
        self.assertEqual(Item.objects.count(), 0)

    def test_for_invalid_input_renders_list_template(self):
        """тест на недопустимый ввод: отображается шаблон списка"""
        response = self.post_invalid_input()
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'lists/list.html')

    def test_for_invalid_input_passes_form_to_template(self):
        """тест на недопустимый ввод: форма передается в шаблон"""
        response = self.post_invalid_input()
        self.assertIsInstance(response.context['form'], ExistingListItemForm)

    def test_for_invalid_input_shows_error_on_page(self):
        """тест на недопустимый ввод: на странице показывается ошибка"""
        response = self.post_invalid_input()
        self.assertContains(response, escape(EMPTY_ITEM_ERROR))

    def test_passes_correct_list_to_template(self):
        """тест: предается правильный шаблон списка"""
        other_list = List.objects.create()
        correct_list = List.objects.create()
        response = self.client.get(f'/lists/{correct_list.id}/')
        self.assertEqual(response.context['list'], correct_list)

    def test_uses_list_template(self):
        """тест: используется шаблон списка"""
        list_ = List.objects.create()
        response = self.client.get(f'/lists/{list_.id}/')
        self.assertTemplateUsed(response, 'lists/list.html')

    def test_displays_only_items_for_that_list(self):
        """тест: отображаются элементы только для этого списка"""
        correct_list = List.objects.create()
        Item.objects.create(text='itemey 1', list=correct_list)
        Item.objects.create(text='itemey 2', list=correct_list)
        other_list = List.objects.create()
        Item.objects.create(text='другой элемент 1 списка', list=other_list)
        Item.objects.create(text='другой элемент 2 списка', list=other_list)

        response = self.client.get(f'/lists/{correct_list.id}/')

        self.assertContains(response, 'itemey 1')
        self.assertContains(response, 'itemey 2')
        self.assertNotContains(response, 'другой элемент 1 списка')
        self.assertNotContains(response, 'другой элемент 2 списка')

    def test_can_save_a_POST_request_to_an_existing_list(self):
        """тест: можно сохранить post-запрос в существующий список"""
        other_list = List.objects.create()
        correct_list = List.objects.create()

        self.client.post(
            f'/lists/{correct_list.id}/',
            data={'text': 'A new item for an existing list'}
        )
        self.assertEqual(Item.objects.count(), 1)
        new_item = Item.objects.first()
        self.assertEqual(new_item.text, 'A new item for an existing list')
        self.assertEqual(new_item.list, correct_list)

    def test_POST_redirects_to_list_view(self):
        """тест: post-запрос переадресуется в представление списка"""
        other_list = List.objects.create()
        correct_list = List.objects.create()

        response = self.client.post(
            f'/lists/{correct_list.id}/',
            data={'text': 'A new item for an existing list'}
        )

        self.assertRedirects(response, f'/lists/{correct_list.id}/')


class HomePageTest(TestCase):
    """Тест домашней страницы"""

    def test_uses_home_template(self):
        """тест: используется домашний шаблон"""
        response = self.client.get('/')
        self.assertTemplateUsed(response, 'lists/home.html')

    def test_home_page_uses_item_form(self):
        """тест: домашняя страница использует форму для элемента"""
        response = self.client.get('/')
        self.assertIsInstance(response.context['form'], ItemForm)
