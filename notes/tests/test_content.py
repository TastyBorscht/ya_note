from datetime import datetime, timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from notes.forms import NoteForm
from notes.models import Note

User = get_user_model()


class TestListPage(TestCase):  # Балк криейт.

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Заметчик')
        for i in range(10):
            cls.notes = Note.objects.create(
                title=f'Название заметки {i}',
                text=f'Просто текст {i}.',
                author=cls.author
            )

    def test_author_got_his_slug(self):
        """ Проверка генерации slug из title."""
        test_slugs = [f'nazvanie-zametki-{i}' for i in range(10)]
        self.client.force_login(self.author)
        all_slugs = [note.slug for note in self.client.get(
            reverse('notes:list')).context['object_list']]
        self.assertEqual(test_slugs, all_slugs)
