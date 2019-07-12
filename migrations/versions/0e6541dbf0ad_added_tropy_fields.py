"""added tropy fields

Revision ID: 0e6541dbf0ad
Revises: be227523f328
Create Date: 2019-06-25 16:01:50.031582

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '0e6541dbf0ad'
down_revision = 'be227523f328'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('pics', sa.Column('archive', sa.VARCHAR(length=250), nullable=True))
    op.add_column('pics', sa.Column('folder', sa.VARCHAR(length=250), nullable=True))
    op.add_column('pics', sa.Column('name', sa.String(length=140), nullable=True))
    op.drop_column('pics', 'tagged')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('pics', sa.Column('tagged', mysql.TINYINT(display_width=1), autoincrement=False, nullable=True))
    op.drop_column('pics', 'name')
    op.drop_column('pics', 'folder')
    op.drop_column('pics', 'archive')
    # ### end Alembic commands ###
