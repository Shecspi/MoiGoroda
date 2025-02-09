from django.urls import reverse
from rest_framework.test import APIClient

from tests.create_db import create_user


def test__get_category_has_correct_log_records(django_user_model, caplog):
    create_user(django_user_model, 1)
    client = APIClient()
    client.login(username='username1', password='password')
    client.get(reverse('category_of_place'), format='json', charset='utf-8')

    assert caplog.records[0].levelname == 'INFO'
    assert (
        caplog.records[0].getMessage()
        == '(API: Place): Getting a list of categories   /api/place/category/'
    )
