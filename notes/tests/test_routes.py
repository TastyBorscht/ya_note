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
        cls.notes_edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.notes_delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.notes_list_url = reverse('notes:list')
        cls.notes_add_url = reverse('notes:add')
        cls.users_login_url = reverse('users:login')
        cls.users_logout_url = reverse('users:logout')
        cls.users_signup_url = reverse('users:signup')
        cls.home_url = reverse('notes:home')
        cls.success_url = reverse('notes:success')
        cls.notes_detail_url = reverse('notes:detail', args=(cls.note.slug,))

    def test_pages_availability(self):
        """Тест доступности страниц для не
        аутентифицированного пользователя.
        """
        reversed_urls = (
            self.home_url,
            self.users_login_url,
            self.users_logout_url,
            self.users_signup_url,
        )
        for url in reversed_urls:
            with self.subTest(url=url):
                self.assertEqual(
                    self.client.get(url).status_code,
                    HTTPStatus.OK
                )

    def test_pages_availability_for_auth_user(self):
        """Тест доступности страниц для аутентифицированного пользователя."""
        reversed_urls = (
            self.notes_list_url,
            self.notes_add_url,
            self.success_url
        )
        for url in reversed_urls:
            with self.subTest(url=url):
                response = self.not_author_client.get(url)
                assert response.status_code == HTTPStatus.OK

    def test_pages_availability_for_different_users(self):
        """Тест доступности страниц для разных пользователей."""
        client_expected_status = (
            (self.not_author_client, HTTPStatus.NOT_FOUND),
            (self.author_client, HTTPStatus.OK)
        )
        reversed_urls = (
            self.notes_detail_url,
            self.notes_delete_url,
            self.notes_edit_url
        )
        for client, status in client_expected_status:
            for url in reversed_urls:
                with self.subTest(
                        client=client, url=url, status=status
                ):
                    response = client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirects(self):
        """Тест редиректа для не аутентифицированного клиента."""
        reversed_urls = (
            self.notes_detail_url,
            self.notes_edit_url,
            self.notes_delete_url,
            self.notes_add_url,
            self.success_url,
            self.notes_list_url
        )
        for url in reversed_urls:
            with self.subTest(url=url):
                expected_url = f'{self.users_login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, expected_url)
