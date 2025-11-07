"""Add social media sources tables

Revision ID: 002
Revises: 001
Create Date: 2025-11-06 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create google_trends_data table
    op.create_table('google_trends_data',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('keyword', sa.String(length=255), nullable=False),
        sa.Column('trend_type', sa.String(length=50), nullable=True),
        sa.Column('data_json', sa.JSON(), nullable=True),
        sa.Column('interest_value', sa.Integer(), nullable=True),
        sa.Column('rank', sa.Integer(), nullable=True),
        sa.Column('geo_region', sa.String(length=10), nullable=True),
        sa.Column('sub_region', sa.String(length=50), nullable=True),
        sa.Column('timeframe', sa.String(length=50), nullable=True),
        sa.Column('trend_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('collected_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_google_trends_data_keyword'), 'google_trends_data', ['keyword'], unique=False)
    op.create_index(op.f('ix_google_trends_data_geo_region'), 'google_trends_data', ['geo_region'], unique=False)
    op.create_index(op.f('ix_google_trends_data_trend_date'), 'google_trends_data', ['trend_date'], unique=False)
    op.create_index('idx_keyword_date', 'google_trends_data', ['keyword', 'trend_date'], unique=False)
    op.create_index('idx_geo_date', 'google_trends_data', ['geo_region', 'trend_date'], unique=False)

    # Create tiktok_content table
    op.create_table('tiktok_content',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('author_username', sa.String(length=255), nullable=True),
        sa.Column('author_nickname', sa.String(length=255), nullable=True),
        sa.Column('author_verified', sa.Boolean(), nullable=True),
        sa.Column('author_follower_count', sa.Integer(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('duration', sa.Integer(), nullable=True),
        sa.Column('music_title', sa.String(length=500), nullable=True),
        sa.Column('views', sa.Integer(), nullable=True),
        sa.Column('likes', sa.Integer(), nullable=True),
        sa.Column('comments', sa.Integer(), nullable=True),
        sa.Column('shares', sa.Integer(), nullable=True),
        sa.Column('engagement_rate', sa.Float(), nullable=True),
        sa.Column('hashtags', sa.JSON(), nullable=True),
        sa.Column('geo_location', sa.String(length=100), nullable=True),
        sa.Column('posted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('collected_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_tiktok_content_author_username'), 'tiktok_content', ['author_username'], unique=False)
    op.create_index('idx_author_posted', 'tiktok_content', ['author_username', 'posted_at'], unique=False)
    op.create_index('idx_engagement', 'tiktok_content', ['engagement_rate'], unique=False)
    op.create_index('idx_posted_at', 'tiktok_content', ['posted_at'], unique=False)

    # Create facebook_content table
    op.create_table('facebook_content',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('page_name', sa.String(length=255), nullable=True),
        sa.Column('author', sa.String(length=255), nullable=True),
        sa.Column('text', sa.Text(), nullable=True),
        sa.Column('post_text', sa.Text(), nullable=True),
        sa.Column('has_image', sa.Boolean(), nullable=True),
        sa.Column('has_video', sa.Boolean(), nullable=True),
        sa.Column('link', sa.String(length=1000), nullable=True),
        sa.Column('post_url', sa.String(length=1000), nullable=True),
        sa.Column('likes', sa.Integer(), nullable=True),
        sa.Column('comments', sa.Integer(), nullable=True),
        sa.Column('shares', sa.Integer(), nullable=True),
        sa.Column('total_engagement', sa.Integer(), nullable=True),
        sa.Column('engagement_score', sa.Float(), nullable=True),
        sa.Column('reactions_json', sa.JSON(), nullable=True),
        sa.Column('images', sa.JSON(), nullable=True),
        sa.Column('video_url', sa.String(length=1000), nullable=True),
        sa.Column('geo_location', sa.String(length=100), nullable=True),
        sa.Column('posted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('collected_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_facebook_content_page_name'), 'facebook_content', ['page_name'], unique=False)
    op.create_index(op.f('ix_facebook_content_posted_at'), 'facebook_content', ['posted_at'], unique=False)
    op.create_index('idx_page_posted', 'facebook_content', ['page_name', 'posted_at'], unique=False)
    op.create_index('idx_engagement_posted', 'facebook_content', ['total_engagement', 'posted_at'], unique=False)

    # Create apify_scraped_data table
    op.create_table('apify_scraped_data',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('platform', sa.String(length=50), nullable=False),
        sa.Column('source_id', sa.String(length=255), nullable=True),
        sa.Column('actor_id', sa.String(length=255), nullable=True),
        sa.Column('run_id', sa.String(length=255), nullable=True),
        sa.Column('author', sa.String(length=255), nullable=True),
        sa.Column('account_name', sa.String(length=255), nullable=True),
        sa.Column('content', sa.Text(), nullable=True),
        sa.Column('content_type', sa.String(length=50), nullable=True),
        sa.Column('metrics_json', sa.JSON(), nullable=True),
        sa.Column('hashtags', sa.JSON(), nullable=True),
        sa.Column('mentions', sa.JSON(), nullable=True),
        sa.Column('media_urls', sa.JSON(), nullable=True),
        sa.Column('raw_data', sa.JSON(), nullable=True),
        sa.Column('location', sa.String(length=255), nullable=True),
        sa.Column('geo_location', sa.String(length=100), nullable=True),
        sa.Column('posted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('collected_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_apify_scraped_data_platform'), 'apify_scraped_data', ['platform'], unique=False)
    op.create_index(op.f('ix_apify_scraped_data_source_id'), 'apify_scraped_data', ['source_id'], unique=False)
    op.create_index(op.f('ix_apify_scraped_data_author'), 'apify_scraped_data', ['author'], unique=False)
    op.create_index('idx_platform_posted', 'apify_scraped_data', ['platform', 'posted_at'], unique=False)
    op.create_index('idx_author_platform', 'apify_scraped_data', ['author', 'platform'], unique=False)
    op.create_index('idx_source_platform', 'apify_scraped_data', ['source_id', 'platform'], unique=False)

    # Create social_media_aggregation table
    op.create_table('social_media_aggregation',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('granularity', sa.String(length=20), nullable=True),
        sa.Column('platform', sa.String(length=50), nullable=True),
        sa.Column('total_posts', sa.Integer(), nullable=True),
        sa.Column('total_videos', sa.Integer(), nullable=True),
        sa.Column('total_trends', sa.Integer(), nullable=True),
        sa.Column('total_views', sa.Integer(), nullable=True),
        sa.Column('total_likes', sa.Integer(), nullable=True),
        sa.Column('total_comments', sa.Integer(), nullable=True),
        sa.Column('total_shares', sa.Integer(), nullable=True),
        sa.Column('avg_engagement_rate', sa.Float(), nullable=True),
        sa.Column('top_hashtags', sa.JSON(), nullable=True),
        sa.Column('top_keywords', sa.JSON(), nullable=True),
        sa.Column('top_authors', sa.JSON(), nullable=True),
        sa.Column('geo_region', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_social_media_aggregation_timestamp'), 'social_media_aggregation', ['timestamp'], unique=False)
    op.create_index(op.f('ix_social_media_aggregation_platform'), 'social_media_aggregation', ['platform'], unique=False)
    op.create_index('idx_timestamp_platform', 'social_media_aggregation', ['timestamp', 'platform'], unique=False)
    op.create_index('idx_timestamp_granularity', 'social_media_aggregation', ['timestamp', 'granularity'], unique=False)

    # Create data_source_monitoring table
    op.create_table('data_source_monitoring',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('source_type', sa.String(length=50), nullable=False),
        sa.Column('source_name', sa.String(length=255), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('last_successful_fetch', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_attempt', sa.DateTime(timezone=True), nullable=True),
        sa.Column('total_items_collected', sa.Integer(), nullable=True),
        sa.Column('items_collected_today', sa.Integer(), nullable=True),
        sa.Column('consecutive_failures', sa.Integer(), nullable=True),
        sa.Column('last_error', sa.Text(), nullable=True),
        sa.Column('error_count', sa.Integer(), nullable=True),
        sa.Column('rate_limit_reset', sa.DateTime(timezone=True), nullable=True),
        sa.Column('requests_remaining', sa.Integer(), nullable=True),
        sa.Column('collection_frequency', sa.Integer(), nullable=True),
        sa.Column('priority', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_data_source_monitoring_source_type'), 'data_source_monitoring', ['source_type'], unique=False)
    op.create_index('idx_source_status', 'data_source_monitoring', ['source_type', 'status'], unique=False)
    op.create_index('idx_last_fetch', 'data_source_monitoring', ['last_successful_fetch'], unique=False)


def downgrade() -> None:
    op.drop_table('data_source_monitoring')
    op.drop_table('social_media_aggregation')
    op.drop_table('apify_scraped_data')
    op.drop_table('facebook_content')
    op.drop_table('tiktok_content')
    op.drop_table('google_trends_data')
