from fastapi import status
from freezegun import freeze_time


def test_get_token(client, user):
    response = client.post(
        '/auth/token',
        data={'username': user.email, 'password': user.plain_password},
    )

    token = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert 'access_token' in token
    assert 'token_type' in token


def test_get_token_wrong_email_without_user(client):
    wrong_email = 'wrong@wrong.com'
    response = client.post(
        '/auth/token',
        data={'username': wrong_email, 'password': 'asdjkasjd'},
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {'detail': 'Incorrect email or password'}


def test_get_token_wrong_email_with_user(client, user):
    wrong_email = 'wrong@wrong.com'
    response = client.post(
        '/auth/token',
        data={'username': wrong_email, 'password': user.plain_password},
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {'detail': 'Incorrect email or password'}


def test_get_token_wrong_password(client, user):
    response = client.post(
        '/auth/token', data={'username': user.email, 'password': 'wrongPass'}
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {'detail': 'Incorrect email or password'}


def test_token_expired_after_time(client, user):
    with freeze_time('2023-10-21 18:00:00'):
        response = client.post(
            '/auth/token',
            data={'username': user.email, 'password': user.plain_password},
        )

        assert response.status_code == status.HTTP_200_OK
        token = response.json()['access_token']

    with freeze_time('2023-10-21 18:31:00'):
        response = client.patch(
            f'/users/{user.id}',
            headers={'Authorization': f'Bearer {token}'},
            json={
                'username': 'wrongwrong',
                'email': 'wrong@wrong.com',
                'password': 'wrong',
            },
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json() == {'detail': 'Could not validate credentials'}


def test_token_expired_dont_refresh(client, user):
    with freeze_time('2023-10-21 12:00:00'):
        response = client.post(
            '/auth/token',
            data={'username': user.email, 'password': user.plain_password},
        )
        assert response.status_code == 200
        token = response.json()['access_token']

    with freeze_time('2023-10-21 12:31:00'):
        response = client.post(
            '/auth/refresh_token',
            headers={'Authorization': f'Bearer {token}'},
        )
        assert response.status_code == 401
        assert response.json() == {'detail': 'Could not validate credentials'}


def test_refresh_token(client, user, token):
    response = client.post(
        '/auth/refresh_token',
        headers={'Authorization': f'Bearer {token}'},
    )

    data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert 'access_token' in data
    assert 'token_type' in data
    assert data['token_type'] == 'bearer'
