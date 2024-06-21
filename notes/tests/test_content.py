from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note

User = get_user_model()


class TestContent(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Довлатов')
        cls.not_author = User.objects.create(username='обычный')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.not_author_client = Client()
        cls.not_author_client.force_login(cls.not_author)
        cls.note = Note.objects.create(
            title='Оригинальный заголовок',
            text='Оригинальный текст',
            slug='original_slug',
            author=cls.author
        )

    def test_notes_list_for_different_users(self):
        """Проверка наличия списка заметок в контексте."""
        clients_note_in_list = (
            (self.author_client, True),
            (self.not_author_client, False),
        )
        for client_, note_in_list in clients_note_in_list:
            with self.subTest(client_=client_, note_in_list=note_in_list):
                response = client_.get(reverse('notes:list'))
                if note_in_list:
                    self.assertIn(self.note, response.context['object_list'])
                else:
                    self.assertNotIn(
                        self.note, response.context['object_list']
                    )

    def test_pages_contains_form(self):
        """Страница редактирования и создания заметки содержат форму."""
        name_args = (
            ('notes:add', None),
            ('notes:edit', (self.note.slug,))
        )
        for name, args in name_args:
            with self.subTest(name=name, args=args):
                response = self.author_client.get(reverse(name, args=args))
                assert 'form' in response.context
                assert isinstance(response.context['form'], NoteForm)
