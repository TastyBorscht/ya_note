from django.contrib.auth import get_user_model

from notes.forms import NoteForm
from notes.tests.test_routes import TestRoutes

User = get_user_model()


class TestContent(TestRoutes):

    def test_notes_list_for_different_users(self):
        """Проверка наличия списка заметок в контексте."""
        clients_asserts = (
            (self.author_client, self.assertIn),
            (self.not_author_client, self.assertNotIn),
        )
        for client_, assert_ in clients_asserts:
            with self.subTest(client_=client_, assert_=assert_):
                response = client_.get(self.notes_list_url)
                assert_(self.note, response.context['object_list'])

    def test_pages_contains_form(self):
        """Страница редактирования и создания заметки содержат форму."""
        reversed_urls = (
            self.notes_edit_url,
            self.notes_add_url,
        )
        for url in reversed_urls:
            with self.subTest(url=url):
                response = self.author_client.get(url)
                assert 'form' in response.context
                assert isinstance(response.context['form'], NoteForm)
