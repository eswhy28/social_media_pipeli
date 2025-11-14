"""Initial migration

Revision ID: 001
Revises:
Create Date: 2025-10-14 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create users table
    op.create_table('users',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('username', sa.String(length=100), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('role', sa.String(length=50), nullable=True),
        sa.Column('permissions', sa.JSON(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)

    # Create social_posts table
    op.create_table('social_posts',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('platform', sa.String(length=50), nullable=False),
        sa.Column('handle', sa.String(length=255), nullable=True),
        sa.Column('text', sa.Text(), nullable=False),
        sa.Column('url', sa.String(length=500), nullable=True),
        sa.Column('likes', sa.Integer(), nullable=True),
        sa.Column('retweets', sa.Integer(), nullable=True),
        sa.Column('replies', sa.Integer(), nullable=True),
        sa.Column('engagement_total', sa.Integer(), nullable=True),
        sa.Column('sentiment', sa.String(length=20), nullable=True),
        sa.Column('sentiment_score', sa.Float(), nullable=True),
        sa.Column('topics', sa.JSON(), nullable=True),
        sa.Column('hashtags', sa.JSON(), nullable=True),
        sa.Column('keywords', sa.JSON(), nullable=True),
        sa.Column('language', sa.String(length=10), nullable=True),
        sa.Column('location', sa.String(length=255), nullable=True),
        sa.Column('state', sa.String(length=100), nullable=True),
        sa.Column('posted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_social_posts_handle'), 'social_posts', ['handle'], unique=False)
    op.create_index('ix_posts_sentiment', 'social_posts', ['sentiment'], unique=False)
    op.create_index('ix_posts_posted_at', 'social_posts', ['posted_at'], unique=False)

    # Create other tables
    op.create_table('hashtags',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tag', sa.String(length=255), nullable=False),
        sa.Column('count', sa.Integer(), nullable=True),
        sa.Column('sentiment_pos', sa.Integer(), nullable=True),
        sa.Column('sentiment_neg', sa.Integer(), nullable=True),
        sa.Column('sentiment_neu', sa.Integer(), nullable=True),
        sa.Column('change_percentage', sa.Float(), nullable=True),
        sa.Column('trending_score', sa.Float(), nullable=True),
        sa.Column('top_posts', sa.JSON(), nullable=True),
        sa.Column('geographic_distribution', sa.JSON(), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_hashtags_tag'), 'hashtags', ['tag'], unique=True)

    # Add more tables as needed...


def downgrade() -> None:
    op.drop_table('hashtags')
    op.drop_table('social_posts')
    op.drop_table('users')

