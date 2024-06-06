from datetime import datetime, timedelta

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone
from pytils.translit import slugify

from notes.forms import NoteForm
from notes.models import Note

User = get_user_model()


class TestListPage(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.TEST_TITLE = 'Название заметки'
        cls.author = User.objects.create(username='Заметчик')
        cls.authorized_user = User.objects.create(username='Незаметчик')
        cls.auth_author_client = Client()
        cls.auth_author_client.force_login(cls.author)
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.authorized_user)
        cls.form_data = {
            'text': 'Тестовая бессмыслица',
            'slug': 'test_slug',
            'title': f'{cls.TEST_TITLE}'
        }
        cls.add_url = reverse('notes:add')

    def test_slug_from_title(self):
        """Проверка генерации slug из title."""
        self.client.force_login(self.author)
        Note.objects.create(
            title=self.TEST_TITLE,
            text='Просто текст',
            author=self.author
        )
        response = self.client.get(self.add_url)
        self.assertEqual(response.context['object_list'][0].slug,
                         slugify(self.TEST_TITLE))

    def test_anonymous_user_cant_create_note(self):
        """Анонимный пользователь не может создавать заметки."""
        self.client.post(self.add_url, data=self.form_data)
        self.assertEqual(Note.objects.count(), 0)

    def test_user_can_create_note(self):
        """Авторизованный пользователь может создавать заметки."""
        response = self.auth_author_client.post(
            self.add_url, data=self.form_data
        )
        self.assertRedirects(response, '/done/')
        self.assertEqual(Note.objects.count(), 1)
        note = Note.objects.get()
        self.assertEqual(note.text, self.form_data['text'])
        self.assertEqual(note.slug, self.form_data['slug'])
        self.assertEqual(note.title, self.form_data['title'])
        self.assertEqual(note.author, self.author)
