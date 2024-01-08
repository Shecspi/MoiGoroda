import pytest

from account.forms import SignUpForm


@pytest.fixture
def setup_db(client, django_user_model):
    django_user_model.objects.create_user(username='username', password='password')


def test__username_exists(setup_db, client):
    data1 = {
        'username': 'username',
        'email': 'username@yaa.ru',
        'password1': 'password',
        'password2': 'password'
    }
    form1 = SignUpForm(data=data1)
    data2 = {
        'username': 'username ',
        'email': 'username@yaa.ru',
        'password1': 'password',
        'password2': 'password'
    }
    form2 = SignUpForm(data=data2)
    data2 = {
        'username': ' username',
        'email': 'username@yaa.ru',
        'password1': 'password',
        'password2': 'password'
    }
    form3 = SignUpForm(data=data2)

    assert not form1.is_valid()
    assert not form2.is_valid()
    assert not form3.is_valid()
