"""изменил подписки на стимид

Revision ID: b39a6e370eb4
Revises: 65a31ed8add9
Create Date: 2025-07-23 19:32:13.624149

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector


# revision identifiers, used by Alembic.
revision: str = 'b39a6e370eb4'
down_revision: Union[str, Sequence[str], None] = '65a31ed8add9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)

    # Get existing constraints and indexes
    fks = inspector.get_foreign_keys('subscriptions')
    indexes = inspector.get_indexes('subscriptions')

    with op.batch_alter_table('subscriptions', recreate='always') as batch_op:
        # First add the new column
        batch_op.add_column(sa.Column('steam_id', sa.Text(), nullable=False))

        # Drop the old index if it exists
        index_names = [idx['name'] for idx in indexes]
        if 'ix_subscriptions_player_id' in index_names:
            batch_op.drop_index('ix_subscriptions_player_id')

        # Create new index
        batch_op.create_index('ix_subscriptions_steam_id', ['steam_id'], unique=False)

        # Drop the foreign key constraint if it exists
        fk_names = [fk['name'] for fk in fks]
        if any(fk['constrained_columns'] == ['player_id'] for fk in fks):
            # Find the exact name of the constraint
            constraint_name = next(
                (fk['name'] for fk in fks if fk['constrained_columns'] == ['player_id']),
                None
            )
            if constraint_name:
                batch_op.drop_constraint(constraint_name, type_='foreignkey')

        # Finally drop the old column
        batch_op.drop_column('player_id')


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table('subscriptions', recreate='always') as batch_op:
        # Add back the old column
        batch_op.add_column(sa.Column('player_id', sa.Integer(), nullable=False))

        # Recreate the foreign key
        batch_op.create_foreign_key(
            'fk_subscriptions_player_id',
            'players',
            ['player_id'],
            ['discord_id']
        )

        # Drop the new index
        batch_op.drop_index('ix_subscriptions_steam_id')

        # Recreate the old index
        batch_op.create_index('ix_subscriptions_player_id', ['player_id'], unique=False)

        # Drop the new column
        batch_op.drop_column('steam_id')