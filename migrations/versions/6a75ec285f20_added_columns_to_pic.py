"""added columns to pic

Revision ID: 6a75ec285f20
Revises: ce7e4eed0272
Create Date: 2019-06-18 16:06:21.761153

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '6a75ec285f20'
down_revision = 'ce7e4eed0272'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('pics', sa.Column('author', sa.VARCHAR(), nullable=True))
    op.add_column('pics', sa.Column('box', sa.VARCHAR(), nullable=True))
    op.add_column('pics', sa.Column('collection', sa.VARCHAR(), nullable=True))
    op.add_column('pics', sa.Column('title', sa.String(length=140), nullable=True))
    op.drop_index('name', table_name='pics')
    op.create_unique_constraint(None, 'pics', ['title'])
    op.drop_column('pics', 'name')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('pics', sa.Column('name', mysql.VARCHAR(length=140), nullable=True))
    op.drop_constraint(None, 'pics', type_='unique')
    op.create_index('name', 'pics', ['name'], unique=True)
    op.drop_column('pics', 'title')
    op.drop_column('pics', 'collection')
    op.drop_column('pics', 'box')
    op.drop_column('pics', 'author')
    # ### end Alembic commands ###
