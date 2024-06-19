from http import HTTPStatus

import pytest
from django.urls import reverse


@pytest.mark.parametrize(
    'name',
    ('notes:home', 'users:login', 'users:logout', 'users:signup')
)
def test_pages_availability_for_anonymous_user(client, name):
    response = client.get(reverse(name))
    assert response.status_code == HTTPStatus.OK
