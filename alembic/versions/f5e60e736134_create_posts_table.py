"""create posts table

Revision ID: f5e60e736134
Revises: 
Create Date: 2023-01-27 19:17:37.151092

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f5e60e736134'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('posts', sa.Column('id', sa.Integer(), nullable = False, primary_key = True)
    , sa.Column('title', sa.String(),nullable = False))
    pass


def downgrade():
    op.drop_table('posts')
    pass
