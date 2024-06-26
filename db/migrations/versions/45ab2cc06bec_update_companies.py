"""Update + Companies

Revision ID: 45ab2cc06bec
Revises: 124c3e0ab3db
Create Date: 2024-05-04 19:19:06.527907

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '45ab2cc06bec'
down_revision: Union[str, None] = '124c3e0ab3db'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('companies',
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=True),
    sa.Column('created_at', sa.TIMESTAMP(), nullable=False),
    sa.Column('updated_at', sa.TIMESTAMP(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.create_table('locations',
    sa.Column('address', sa.String(), nullable=False),
    sa.Column('company_id', sa.Integer(), nullable=True),
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=True),
    sa.Column('created_at', sa.TIMESTAMP(), nullable=False),
    sa.Column('updated_at', sa.TIMESTAMP(), nullable=False),
    sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.add_column('users', sa.Column('location_id', sa.Integer(), nullable=True))
    op.alter_column('users', 'user_id',
               existing_type=sa.BIGINT(),
               nullable=False)
    op.alter_column('users', 'admin',
               existing_type=sa.BOOLEAN(),
               nullable=False)
    op.alter_column('users', 'active',
               existing_type=sa.BOOLEAN(),
               nullable=False)
    op.alter_column('users', 'reg_date',
               existing_type=sa.DATE(),
               nullable=False)
    op.alter_column('users', 'upd_date',
               existing_type=sa.DATE(),
               nullable=False)
    op.alter_column('users', 'id',
               existing_type=sa.INTEGER(),
               nullable=True,
               autoincrement=True)
    op.create_foreign_key(None, 'users', 'locations', ['location_id'], ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'users', type_='foreignkey')
    op.alter_column('users', 'id',
               existing_type=sa.INTEGER(),
               nullable=False,
               autoincrement=True)
    op.alter_column('users', 'upd_date',
               existing_type=sa.DATE(),
               nullable=True)
    op.alter_column('users', 'reg_date',
               existing_type=sa.DATE(),
               nullable=True)
    op.alter_column('users', 'active',
               existing_type=sa.BOOLEAN(),
               nullable=True)
    op.alter_column('users', 'admin',
               existing_type=sa.BOOLEAN(),
               nullable=True)
    op.alter_column('users', 'user_id',
               existing_type=sa.BIGINT(),
               nullable=False)
    op.drop_column('users', 'location_id')
    op.drop_table('locations')
    op.drop_table('companies')
    # ### end Alembic commands ###
