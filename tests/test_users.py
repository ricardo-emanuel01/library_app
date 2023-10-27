from fastapi import status

from library_app.schemas import UserPublic


def test_create_new_user(client):
    response = client.post(
        '/users/',
        json={
            'username': 'mariana',
            'email': 'mariana@example.com',
            'password': 'salgadinhodeuva',
        },
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == {
        'username': 'mariana',
        'email': 'mariana@example.com',
        'id': 1,
    }


def test_create_user_with_existent_email(client, user):
    response = client.post(
        '/users/',
        json={
            'username': 'username',
            'password': 'fizzbyzz',
            'email': user.email,
        },
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {
        'detail': 'Email or username already registered'
    }


def test_create_user_with_existent_username(client, user):
    response = client.post(
        '/users/',
        json={
            'username': user.username,
            'password': 'fizzbyzz',
            'email': 'user@example.com',
        },
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {
        'detail': 'Email or username already registered'
    }


def test_read_users(client):
    response = client.get('/users/')

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {'users': []}


def test_read_users_with_users(client, user):
    user_schema = UserPublic.model_validate(user).model_dump()

    response = client.get('/users/')

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {'users': [user_schema]}


def test_update_user(client, user, token):
    response = client.patch(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'bob',
            'email': 'bob@example.com',
            'password': 'jasdasd',
        },
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        'username': 'bob',
        'email': 'bob@example.com',
        'id': user.id,
    }


def test_update_another_user(client, another_user, token):
    response = client.patch(
        f'/users/{another_user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'bob',
            'email': 'bob@example.com',
            'password': 'jasdasd',
        },
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {'detail': 'Not enough permissions'}


def test_delete_user(client, user, token):
    response = client.delete(
        f'/users/{user.id}', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {'detail': 'User deleted'}


def test_delete_another_user(client, another_user, token):
    response = client.delete(
        f'/users/{another_user.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {'detail': 'Not enough permissions'}
