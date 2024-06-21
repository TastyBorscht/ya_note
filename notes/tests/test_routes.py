from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.not_author = User.objects.create(username='Горький')
        cls.not_author_client = Client()
        cls.not_author_client.force_login(cls.not_author)
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug='note-slug',
            author=cls.author
        )

    def test_pages_availability(self):
        """Тест доступности страниц для не
        аутентифицированного пользователя.
        """
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

    def test_pages_availability_for_auth_user(self):
        """Тест доступности страниц для аутентифицированного пользователя."""
        names = ('notes:list', 'notes:add', 'notes:success')
        for name in names:
            with self.subTest(name=name):
                response = self.not_author_client.get(reverse(name))
                assert response.status_code == HTTPStatus.OK

    def test_pages_availability_for_different_users(self):
        """Тест доступности страниц для разных пользователей."""
        client_expected_status = (
            (self.not_author_client, HTTPStatus.NOT_FOUND),
            (self.author_client, HTTPStatus.OK)
        )
        names = ('notes:detail', 'notes:edit', 'notes:delete')
        for client, status in client_expected_status:
            for name in names:
                with self.subTest(
                        client=client, name=name, status=status
                ):
                    response = client.get(reverse(
                        name, args=(self.note.slug,)))
                    self.assertEqual(response.status_code, status)

    def test_redirects(self):
        """Тест редиректа для не аутентифицированного клиента."""
        name_args = (
            ('notes:detail', (self.note.slug,)),
            ('notes:edit', (self.note.slug,)),
            ('notes:delete', (self.note.slug,)),
            ('notes:add', None),
            ('notes:success', None),
            ('notes:list', None),
        )
        for name, args in name_args:
            with self.subTest(name=name, args=args):
                login_url = reverse('users:login')
                url = reverse(name, args=args)
                expected_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, expected_url)
