from http import HTTPStatus

from django.contrib.auth import get_user_model
from pytest_django.asserts import assertFormError, assertRedirects
from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note
from notes.tests.test_routes import TestRoutes

User = get_user_model()


class TestListPage(TestRoutes):
    TEST_TITLE = 'Название заметки'

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.form_data = {
            'text': 'Тестовая бессмыслица',
            'slug': 'test_slug',
            'title': f'{cls.TEST_TITLE}'
        }

    def test_user_can_create_note(self):
        """Авторизованный пользователь может создавать заметки."""
        Note.objects.all().delete()
        response = self.author_client.post(
            self.notes_add_url, data=self.form_data
        )
        self.assertRedirects(response, self.success_url)
        self.assertEqual(Note.objects.count(), 1)
        note = Note.objects.get()
        self.assertEqual(note.text, self.form_data['text'])
        self.assertEqual(note.slug, self.form_data['slug'])
        self.assertEqual(note.title, self.form_data['title'])
        self.assertEqual(note.author, self.author)

    def test_anonymous_user_cant_create_note(self):
        """Анонимный пользователь не может создавать заметки."""
        Note.objects.all().delete()
        response = self.client.post(self.notes_add_url, data=self.form_data)
        expected_url = f'{self.users_login_url}?next={self.notes_add_url}'
        self.assertRedirects(response, expected_url)
        self.assertEqual(Note.objects.count(), 0)

    def test_not_unique_slug(self):
        """Нельзя создать две заметки с одинаковым 'slug'."""
        self.form_data['slug'] = self.note.slug
        notes_count = Note.objects.count()
        response = self.author_client.post(
            self.notes_add_url,
            data=self.form_data
        )
        self.assertEqual(Note.objects.count(), notes_count)
        assertFormError(
            response,
            'form',
            'slug',
            errors=(self.note.slug + WARNING)
        )

    def test_empty_slug(self):
        """Slug создается из 'title' если поле пустое."""
        self.form_data.pop('slug')
        Note.objects.all().delete()
        response = self.author_client.post(
            self.notes_add_url,
            data=self.form_data
        )
        assertRedirects(response, self.success_url)
        self.assertEqual(Note.objects.count(), 1)
        self.assertEqual(
            Note.objects.get().slug, slugify(self.form_data['title'])
        )


class TestNoteEditDelete(TestRoutes):
    NOTE_TEXT = 'Текст'
    NEW_NOTE_TEXT = 'Обновлённая заметка'
    NOTE_SLUG = 'note-slug'
    NOTE_TITLE = 'Заголовок'

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.form_data = {
            'text': cls.NEW_NOTE_TEXT,
            'title': cls.NOTE_TITLE,
            'author': cls.author,
        }

    def test_author_can_edit_notes(self):
        """Автор может редактировать заметки."""
        self.author_client.post(
            self.notes_edit_url,
            data=self.form_data
        )
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.form_data['text'])
        self.assertEqual(self.note.author, self.form_data['author'])
        self.assertEqual(self.note.title, self.form_data['title'])

    def test_other_user_cant_edit_note(self):
        """Не автор не может редактировать заметки."""
        old_note = Note.objects.get(id=self.note.id)
        response = self.not_author_client.post(
            self.notes_edit_url,
            data=self.form_data
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(self.note.text, old_note.text)
        self.assertEqual(self.note.title, old_note.title)
        self.assertEqual(self.note.author, old_note.author)

    def test_author_can_delete_note(self):
        """Автор может удалить свою заметку."""
        notes_count = Note.objects.count()
        if notes_count == 0:
            self.author_client.post(
                self.notes_add_url,
                data=self.form_data
            )
        response = self.author_client.delete(self.notes_delete_url)
        self.assertRedirects(response, self.success_url)
        self.assertEqual(Note.objects.count(), notes_count - 1)

    def test_user_cant_delete_note_of_another_user(self):
        """Пользователь не может удалить чужую заметку."""
        notes_count = Note.objects.count()
        if notes_count == 0:
            self.author_client.post(
                self.notes_add_url,
                data=self.form_data
            )
        response = self.not_author_client.delete(self.notes_delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), notes_count)
