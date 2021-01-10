"""empty message

Revision ID: e12f058fc3d1
Revises: 16ebe42fb965
Create Date: 2020-10-13 22:09:57.114866

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e12f058fc3d1'
down_revision = '16ebe42fb965'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Venue', sa.Column('genres', sa.String(length=120), nullable=True))
    op.drop_column('Venue', 'generes')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Venue', sa.Column('generes', sa.VARCHAR(length=120), autoincrement=False, nullable=True))
    op.drop_column('Venue', 'genres')
    # ### end Alembic commands ###
