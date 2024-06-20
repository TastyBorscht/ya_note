from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class TestAdd(TestCase):

    def setUp(self):
        self.user = User.objects.create(username='Karabas-barabas')

    def authorized_user_get_form(self):
        """Авторизованный пользователь получает форму создания заметки."""
        self.assertIn(
            'form',
            self.client.force_login(self.user).get(
                reverse('notes:add')).context
        )
