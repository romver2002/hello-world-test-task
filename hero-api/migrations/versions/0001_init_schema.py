"""init schema

Revision ID: 0001_init
Revises: 
Create Date: 2025-08-11 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0001_init'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'heroes',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=120), nullable=False),
        sa.Column('intelligence', sa.Integer(), nullable=True),
        sa.Column('strength', sa.Integer(), nullable=True),
        sa.Column('speed', sa.Integer(), nullable=True),
        sa.Column('power', sa.Integer(), nullable=True),
        sa.UniqueConstraint('name', name='uq_hero_name'),
    )
    op.create_index('ix_heroes_name', 'heroes', ['name'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_heroes_name', table_name='heroes')
    op.drop_table('heroes')


