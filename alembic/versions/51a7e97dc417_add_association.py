"""Add association

Revision ID: 51a7e97dc417
Revises:
Create Date: 2015-05-28 07:40:54.985907

"""

# revision identifiers, used by Alembic.
revision = '51a7e97dc417'
down_revision = None
branch_labels = None
depends_on = None

from alembic import op
from sqlalchemy import Column, String, Integer


def upgrade():
    op.add_column('report', Column('association', String(120)))
    op.alter_column('report', 'comments', type_=String(2000), existing_type=String(length=120))

    op.add_column('event', Column('people_involved', Integer()))


def downgrade():
    op.drop_column('report', 'association')
    op.alter_column('report', 'comments', type_=String(120), existing_type=String(length=2000))

    op.drop_column('event', 'people_involved')
