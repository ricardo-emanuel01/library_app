from sqlalchemy import select

from library_app.models import User


def test_create_user(session):
    test_name = 'mariana'
    new_user = User(
        username=test_name,
        password='segredo',
        email='mari@test.com',
        genre1='action',
        genre2='adventure',
    )

    session.add(new_user)
    session.commit()

    user = session.scalar(select(User).where(User.username == test_name))

    assert user.username == test_name
