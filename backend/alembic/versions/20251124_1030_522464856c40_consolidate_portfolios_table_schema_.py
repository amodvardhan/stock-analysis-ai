"""Consolidate portfolios table schema - ensure correct columns

Revision ID: 522464856c40
Revises: 2f46b23ff531
Create Date: 2025-11-24 10:30:22.955283+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '522464856c40'
down_revision: Union[str, None] = None  # Base migration - consolidates all previous portfolio schema changes
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Consolidated migration to ensure portfolios table has correct schema.
    
    This migration:
    1. Ensures all correct columns exist (from Portfolio model)
    2. Removes all incorrect columns (that belong to other tables)
    
    Correct columns for portfolios table:
    - id (primary key, auto-increment)
    - user_id (foreign key to users)
    - name (VARCHAR(100), NOT NULL, default='My Portfolio')
    - description (TEXT, nullable)
    - total_invested (DECIMAL(15, 2), default=0.0)
    - current_value (DECIMAL(15, 2), default=0.0)
    - total_return (DECIMAL(15, 2), default=0.0)
    - return_percentage (FLOAT, default=0.0)
    - created_at (DateTime, NOT NULL)
    - updated_at (DateTime, NOT NULL)
    - last_updated (DateTime, NOT NULL)
    """
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    columns = [col['name'] for col in inspector.get_columns('portfolios')]
    
    # ============================================================================
    # STEP 1: Ensure all correct columns exist
    # ============================================================================
    
    # Portfolio details
    if 'name' not in columns:
        op.add_column('portfolios', 
                      sa.Column('name', sa.String(100), nullable=False, server_default='My Portfolio'))
    
    if 'description' not in columns:
        op.add_column('portfolios', 
                      sa.Column('description', sa.Text(), nullable=True))
    
    # Portfolio metrics
    if 'total_invested' not in columns:
        op.add_column('portfolios', 
                      sa.Column('total_invested', sa.DECIMAL(15, 2), nullable=False, server_default='0.00'))
    
    if 'current_value' not in columns:
        op.add_column('portfolios', 
                      sa.Column('current_value', sa.DECIMAL(15, 2), nullable=False, server_default='0.00'))
    
    if 'total_return' not in columns:
        op.add_column('portfolios', 
                      sa.Column('total_return', sa.DECIMAL(15, 2), nullable=False, server_default='0.00'))
    
    if 'return_percentage' not in columns:
        op.add_column('portfolios', 
                      sa.Column('return_percentage', sa.Float(), nullable=False, server_default='0.0'))
    
    # Timestamps
    if 'created_at' not in columns:
        op.add_column('portfolios', 
                      sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()))
    
    if 'updated_at' not in columns:
        op.add_column('portfolios', 
                      sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()))
    
    if 'last_updated' not in columns:
        op.add_column('portfolios', 
                      sa.Column('last_updated', sa.DateTime(), nullable=False, server_default=sa.func.now()))
    
    # ============================================================================
    # STEP 2: Remove all incorrect columns
    # ============================================================================
    
    # Columns that belong to portfolio_holdings (not portfolios)
    holding_columns = [
        'stock_id',
        'quantity',
        'average_buy_price',
        'current_price',  # Individual stock price, not portfolio total
        'unrealized_pl',
        'unrealized_pl_percentage',
        'realized_pl',
        'first_buy_date'
    ]
    
    # Columns that belong to portfolio_transactions (not portfolios)
    transaction_columns = [
        'purchase_price',
        'purchase_date',
        'price_per_share',
        'transaction_date',
        'brokerage_fee',
        'tax',
        'notes',
        'total_amount',
        'other_charges'
    ]
    
    # Combine all incorrect columns
    incorrect_columns = holding_columns + transaction_columns
    
    # Remove incorrect columns
    for col_name in incorrect_columns:
        if col_name in columns:
            # Check for foreign key constraints first
            foreign_keys = inspector.get_foreign_keys('portfolios')
            for fk in foreign_keys:
                if col_name in fk['constrained_columns']:
                    op.drop_constraint(fk['name'], 'portfolios', type_='foreignkey')
            
            # Drop the column
            op.drop_column('portfolios', col_name)


def downgrade() -> None:
    """
    Downgrade is intentionally minimal as this migration ensures schema correctness.
    Reverting would require knowing the previous incorrect state, which we don't want.
    """
    pass
