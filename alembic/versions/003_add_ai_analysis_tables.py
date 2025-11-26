"""Add all social media and AI analysis tables

Revision ID: 003
Revises: 002
Create Date: 2025-11-26 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create AI analysis tables
    
    # apify_data_processing_status
    op.create_table('apify_data_processing_status',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('scraped_data_id', sa.String(), nullable=False),
        sa.Column('processing_stage', sa.String(length=50), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('retry_count', sa.Integer(), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_scraped_data_status', 'apify_data_processing_status', ['scraped_data_id', 'status'])
    op.create_index('idx_processing_stage', 'apify_data_processing_status', ['processing_stage', 'status'])
    
    # apify_sentiment_analysis
    op.create_table('apify_sentiment_analysis',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('scraped_data_id', sa.String(), nullable=False),
        sa.Column('sentiment', sa.String(length=20), nullable=True),
        sa.Column('confidence', sa.Float(), nullable=True),
        sa.Column('positive_score', sa.Float(), nullable=True),
        sa.Column('negative_score', sa.Float(), nullable=True),
        sa.Column('neutral_score', sa.Float(), nullable=True),
        sa.Column('subjectivity', sa.Float(), nullable=True),
        sa.Column('emotion', sa.String(length=50), nullable=True),
        sa.Column('emotion_scores', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_sentiment_scraped_id', 'apify_sentiment_analysis', ['scraped_data_id'])
    op.create_index('idx_sentiment_type', 'apify_sentiment_analysis', ['sentiment'])
    
    # apify_location_extractions
    op.create_table('apify_location_extractions',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('scraped_data_id', sa.String(), nullable=False),
        sa.Column('location_text', sa.String(length=255), nullable=True),
        sa.Column('location_type', sa.String(length=50), nullable=True),
        sa.Column('confidence', sa.Float(), nullable=True),
        sa.Column('country', sa.String(length=100), nullable=True),
        sa.Column('state', sa.String(length=100), nullable=True),
        sa.Column('city', sa.String(length=100), nullable=True),
        sa.Column('coordinates', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_location_scraped_id', 'apify_location_extractions', ['scraped_data_id'])
    op.create_index('idx_location_city', 'apify_location_extractions', ['city'])
    op.create_index('idx_location_state', 'apify_location_extractions', ['state'])
    
    # apify_entity_extractions
    op.create_table('apify_entity_extractions',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('scraped_data_id', sa.String(), nullable=False),
        sa.Column('entity_text', sa.String(length=255), nullable=True),
        sa.Column('entity_type', sa.String(length=50), nullable=True),
        sa.Column('confidence', sa.Float(), nullable=True),
        sa.Column('start_pos', sa.Integer(), nullable=True),
        sa.Column('end_pos', sa.Integer(), nullable=True),
        sa.Column('context', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_entity_scraped_id', 'apify_entity_extractions', ['scraped_data_id'])
    op.create_index('idx_entity_type', 'apify_entity_extractions', ['entity_type'])
    op.create_index('idx_entity_text', 'apify_entity_extractions', ['entity_text'])
    
    # apify_keyword_extractions
    op.create_table('apify_keyword_extractions',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('scraped_data_id', sa.String(), nullable=False),
        sa.Column('keyword', sa.String(length=100), nullable=True),
        sa.Column('score', sa.Float(), nullable=True),
        sa.Column('frequency', sa.Integer(), nullable=True),
        sa.Column('keyword_type', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_keyword_scraped_id', 'apify_keyword_extractions', ['scraped_data_id'])
    op.create_index('idx_keyword', 'apify_keyword_extractions', ['keyword'])
    op.create_index('idx_keyword_score', 'apify_keyword_extractions', ['score'])
    
    # apify_ai_batch_jobs
    op.create_table('apify_ai_batch_jobs',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('job_type', sa.String(length=50), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('total_records', sa.Integer(), nullable=True),
        sa.Column('processed_records', sa.Integer(), nullable=True),
        sa.Column('failed_records', sa.Integer(), nullable=True),
        sa.Column('error_log', sa.JSON(), nullable=True),
        sa.Column('config', sa.JSON(), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_batch_status', 'apify_ai_batch_jobs', ['status', 'job_type'])


def downgrade() -> None:
    # Drop AI analysis tables
    op.drop_index('idx_batch_status', table_name='apify_ai_batch_jobs')
    op.drop_table('apify_ai_batch_jobs')
    
    op.drop_index('idx_keyword_score', table_name='apify_keyword_extractions')
    op.drop_index('idx_keyword', table_name='apify_keyword_extractions')
    op.drop_index('idx_keyword_scraped_id', table_name='apify_keyword_extractions')
    op.drop_table('apify_keyword_extractions')
    
    op.drop_index('idx_entity_text', table_name='apify_entity_extractions')
    op.drop_index('idx_entity_type', table_name='apify_entity_extractions')
    op.drop_index('idx_entity_scraped_id', table_name='apify_entity_extractions')
    op.drop_table('apify_entity_extractions')
    
    op.drop_index('idx_location_state', table_name='apify_location_extractions')
    op.drop_index('idx_location_city', table_name='apify_location_extractions')
    op.drop_index('idx_location_scraped_id', table_name='apify_location_extractions')
    op.drop_table('apify_location_extractions')
    
    op.drop_index('idx_sentiment_type', table_name='apify_sentiment_analysis')
    op.drop_index('idx_sentiment_scraped_id', table_name='apify_sentiment_analysis')
    op.drop_table('apify_sentiment_analysis')
    
    op.drop_index('idx_processing_stage', table_name='apify_data_processing_status')
    op.drop_index('idx_scraped_data_status', table_name='apify_data_processing_status')
    op.drop_table('apify_data_processing_status')

