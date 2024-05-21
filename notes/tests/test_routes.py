from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.reader = User.objects.create(username='Читатель простой')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=cls.author
        )

    def test_pages_availability(self):
        urls = (
            'notes:home',
            'users:login',
            'users:logout',
            'users:signup',
        )
        for name in urls:
            with self.subTest(name=name):
                self.assertEqual(
                    self.client.get(reverse(name, args)).status_code,
                    HTTPStatus.OK
                )

    # def test_availability_for_comment_edit_and_delete(self):
    #     users_statuses = (
    #         (self.author, HTTPStatus.OK),
    #         (self.reader, HTTPStatus.NOT_FOUND),
    #     )
    #     for user, status in users_statuses:
    #         self.client.force_login(user)
    #         for name in ('news:edit', 'news:delete'):
    #             with self.subTest(user=user, name=name):
    #                 url = reverse(name, args=(self.comment.id,))
    #                 response = self.client.get(url)
    #                 self.assertEqual(response.status_code, status)
    #
    # def test_redirect_for_anonymous_client(self):
    #     for name in ('news:edit', 'news:delete'):
    #         with self.subTest(name=name):
    #             url = reverse(name, args=(self.comment.id,))
    #             response = self.client.get(url)
    #             self.assertRedirects(response, f'{reverse('users:login')}?next={url}')
