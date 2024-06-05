from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class TestAdd(TestCase):

    def setUp(self):
        self.user = User.objects.create(username='Karabas-barabas')

    def authorized_user_get_form(self):
        """Авторизированный пользователь получает форму создания заметки."""
        self.assertIn(
            'form',
            self.client.force_login(self.user).get(
                reverse('notes:add')).context
        )

from datetime import datetime, timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from pytils.translit import slugify

from notes.forms import NoteForm
from notes.models import Note

User = get_user_model()


# class TestListPage(TestCase):
#
#     @classmethod
#     def setUpTestData(cls):
#         cls.TEST_TITLE = 'Название заметки'
#         cls.author = User.objects.create(username='Заметчик')
#         for i in range(3):
#             cls.notes = Note.objects.create(
#                 title=f'{cls.TEST_TITLE} {i}',
#                 text=f'Просто текст {i}.',
#                 author=cls.author
#             )
#
#     def test_author_got_his_slug(self):
#         """ Проверка генерации slug из title."""
#         test_slugs = [f'{slugify(self.TEST_TITLE)}-{i}' for i in range(3)]
#         self.client.force_login(self.author)
#         all_slugs = [note.slug for note in self.client.get(
#             reverse('notes:list')).context['object_list']]
#         self.assertEqual(test_slugs, all_slugs)