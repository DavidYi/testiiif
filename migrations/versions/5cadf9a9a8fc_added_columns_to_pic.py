"""added columns to pic

Revision ID: 5cadf9a9a8fc
Revises: 6a75ec285f20
Create Date: 2019-06-18 16:08:35.500645

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '5cadf9a9a8fc'
down_revision = '6a75ec285f20'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('pics', sa.Column('author', sa.VARCHAR(length=250), nullable=True))
    op.add_column('pics', sa.Column('box', sa.VARCHAR(length=250), nullable=True))
    op.add_column('pics', sa.Column('collection', sa.VARCHAR(length=250), nullable=True))
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
