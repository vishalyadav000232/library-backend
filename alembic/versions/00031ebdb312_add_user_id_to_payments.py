"""add user_id to payments

Revision ID: 00031ebdb312
Revises: a3758836ca55
Create Date: 2026-04-27 07:29:34.160750

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '00031ebdb312'
down_revision: Union[str, Sequence[str], None] = 'a3758836ca55'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


def upgrade() -> None:
    bind = op.get_bind()

    # ✅ STEP 1: Create ENUM safely
    payment_status_enum = postgresql.ENUM(
        'CREATED', 'SUCCESS', 'FAILED',
        name='paymentstatus'
    )
    payment_status_enum.create(bind, checkfirst=True)

    # ✅ STEP 2: Add user_id as nullable first
    op.add_column(
        'payments',
        sa.Column('user_id', sa.UUID(), nullable=True)
    )

    # ✅ STEP 3: Backfill user_id (IMPORTANT)
    op.execute("""
        UPDATE payments
        SET user_id = (
            SELECT user_id FROM bookings WHERE bookings.id = payments.booking_id
        )
    """)

    # ✅ STEP 4: Make NOT NULL
    op.alter_column('payments', 'user_id', nullable=False)

    # ✅ STEP 5: Normalize old status values
    op.execute("UPDATE payments SET status = 'SUCCESS' WHERE status = 'verified'")
    op.execute("UPDATE payments SET status = 'CREATED' WHERE status = 'pending'")
    op.execute("UPDATE payments SET status = 'FAILED' WHERE status = 'failed'")

    # ✅ STEP 6: Convert VARCHAR → ENUM (IMPORTANT)
    op.execute("""
        ALTER TABLE payments
        ALTER COLUMN status TYPE paymentstatus
        USING status::paymentstatus
    """)

    # ✅ STEP 7: Constraints (give names — good practice)
    op.create_unique_constraint(
        "uq_provider_payment_id",
        "payments",
        ["provider_payment_id"]
    )

    op.create_foreign_key(
        "fk_payments_user_id",
        "payments",
        "users",
        ["user_id"],
        ["id"]
    )

def downgrade() -> None:
    op.drop_constraint("fk_payments_user_id", "payments", type_='foreignkey')
    op.drop_constraint("uq_provider_payment_id", "payments", type_='unique')

    op.execute("""
        ALTER TABLE payments
        ALTER COLUMN status TYPE VARCHAR
    """)

    op.drop_column('payments', 'user_id')

    op.execute("DROP TYPE IF EXISTS paymentstatus")