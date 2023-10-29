"""updated users table to support favorite genres

Revision ID: da4d6e6e463c
Revises: d8b39478729f
Create Date: 2023-10-29 09:55:02.747932

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'da4d6e6e463c'
down_revision: Union[str, None] = 'd8b39478729f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('genre1', sa.String(), nullable=False))
    op.add_column('users', sa.Column('genre2', sa.String(), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'genre2')
    op.drop_column('users', 'genre1')
    # ### end Alembic commands ###
