from fastapi import status


def test_read_books_empty(client, user, token):
    response = client.get(
        '/book', headers={'Authorization': f'Bearer {token}'}
    )

    response.status_code == status.HTTP_200_OK
    response.json() == {}


def test_read_books_not_empty(client, user, token):
    pass


def tes_read_books_no_authorization(client, user, another_user, token):
    pass
