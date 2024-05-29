from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой', password='123test')
        cls.reader = User.objects.create(username='Читатель простой', password='123test')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=cls.author
        )
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)

    def test_pages_availability(self):
        """Тест доступности страниц для не аутентифицированного пользователя."""
        urls = (
            'notes:home',
            'users:login',
            'users:logout',
            'users:signup',
        )
        for name in urls:
            with self.subTest(name=name):
                self.assertEqual(
                    self.client.get(reverse(name)).status_code,
                    HTTPStatus.OK
                )

    def test_redirect_for_anonymous_client(self):
        """Тест редиректа на страницу авторизации для
        не аутентифицированного пользователя."""
        login_url = reverse('users:login')
        urls = (
            ('notes:add', None),
            ('notes:edit', (self.note.id,)),
            ('notes:detail', (self.note.id,)),
            ('notes:delete', (self.note.id,)),
            ('notes:list', None),
            ('notes:success', None),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                redirect_url = f'{login_url}?next={url}'
                self.assertRedirects(
                    response, redirect_url
                )

    def test_redirect_note_update(self):
        """Тест редиректа после редактирования заметки."""
        response = self.author_client.post(
            reverse('notes:edit', args=(self.note.slug,)), {
                'title': 'Test_edit_title',
                'text': 'Test_edit_text',
            }
        )
        self.assertRedirects(response, reverse('notes:success'))

    def test_redirect_note_create(self):
        """Тест редиректа после создания заметки."""
        response = self.author_client.post(
            reverse('notes:add'), {
                'title': 'Test_new_title',
                'text': 'Test_new_text'
            }
        )
        self.assertRedirects(response, reverse('notes:success'))

    def test_redirect_note_create(self):
        """Тест редиректа после удаления заметки."""
        response = self.author_client.delete(
            reverse('notes:delete', args=(self.note.slug,))
        )
        self.assertRedirects(response, reverse('notes:success'))
