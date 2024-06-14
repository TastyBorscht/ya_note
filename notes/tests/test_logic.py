from datetime import datetime, timedelta
from http import HTTPStatus

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

    def test_slug_from_title(self):
        """Проверка генерации slug из title."""
        Note.objects.create(
            title=self.TEST_TITLE,
            text='Просто текст',
            author=self.author
        )
        response = self.auth_author_client.get(reverse('notes:list'))
        self.assertEqual(response.context['object_list'][0].slug,
                         slugify(self.TEST_TITLE))

    def test_anonymous_user_cant_create_note(self):
        """Анонимный пользователь не может создавать заметки."""
        self.client.post(reverse('notes:add'), data=self.form_data)
        self.assertEqual(Note.objects.count(), 0)

    def test_user_can_create_note(self):
        """Авторизованный пользователь может создавать заметки."""
        response = self.auth_author_client.post(
            reverse('notes:add'), data=self.form_data
        )
        self.assertRedirects(response, '/done/')
        self.assertEqual(Note.objects.count(), 1)
        note = Note.objects.get()
        self.assertEqual(note.text, self.form_data['text'])
        self.assertEqual(note.slug, self.form_data['slug'])
        self.assertEqual(note.title, self.form_data['title'])
        self.assertEqual(note.author, self.author)


class TestNoteEditDelete(TestCase):
    NOTE_TEXT = 'Текст заметки'
    NEW_NOTE_TEXT = 'Обновлённая заметка'
    NOTE_SLUG = 'test_slug'
    NOTE_TITLE = 'test_title'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор заметки')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader = User.objects.create(username='Читатель')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.note = Note.objects.create(
            text=cls.NOTE_TEXT,
            author=cls.author,
            slug=cls.NOTE_SLUG,
            title=cls.NOTE_TITLE
        )
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.success_url = reverse('notes:success')
        cls.form_data = {
            'text': cls.NEW_NOTE_TEXT,
            'title': cls.NOTE_TITLE
        }

    def test_author_can_edit_notes(self):
        """Автор может редактировать заметки."""
        self.author_client.post(
            self.edit_url,
            data=self.form_data
        )
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.NEW_NOTE_TEXT)

    def test_user_cant_edit_note_of_another_user(self):
        """Не автор не может редактировать заметки."""
        response = self.reader_client.post(self.edit_url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.NOTE_TEXT)

    def test_author_can_delete_note(self):
        """Автор может удалить свою заметку."""
        response = self.author_client.delete(self.delete_url)
        self.assertRedirects(response, self.success_url)
        self.assertEqual(Note.objects.count(), 0)

    def test_user_cant_delete_note_of_another_user(self):
        """Пользователь не может удалить чужую заметку."""
        response = self.reader_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(Note.objects.count(), 1)
