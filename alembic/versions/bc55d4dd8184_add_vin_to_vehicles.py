"""add vin to vehicles

Revision ID: bc55d4dd8184
Revises: bfb6a6a2e86b
Create Date: 2025-12-08 13:14:12.461240

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "bc55d4dd8184"
down_revision: Union[str, Sequence[str], None] = "bfb6a6a2e86b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # On supprime l'index sur timestamp (si encore présent)
    op.drop_index(op.f("ix_vehicle_status_timestamp"), table_name="vehicle_status")

    # Colonnes ajoutées / modifiées sur vehicles
    op.add_column("vehicles", sa.Column("nickname", sa.String(), nullable=True))
    op.add_column(
        "vehicles",
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )

    # external_id devient nullable
    op.alter_column(
        "vehicles",
        "external_id",
        existing_type=sa.VARCHAR(),
        nullable=True,
    )

    # ⚠️ vin : on utilise un ALTER TABLE ... IF NOT EXISTS pour
    # éviter l'erreur "column vin already exists" si la migration
    # a déjà été partiellement appliquée.
    op.execute(
        "ALTER TABLE vehicles "
        "ADD COLUMN IF NOT EXISTS vin VARCHAR(64);"
    )

    # On supprime l’ancienne colonne name
    op.drop_column("vehicles", "name")

    # IMPORTANT : corriger les valeurs NULL avant de rendre la colonne NOT NULL
    op.execute(
        "UPDATE vehicle_status SET is_plugged = FALSE WHERE is_plugged IS NULL"
    )

    # Maintenant, on peut appliquer la contrainte NOT NULL
    op.alter_column(
        "vehicle_status",
        "is_plugged",
        existing_type=sa.BOOLEAN(),
        nullable=False,
        existing_nullable=True,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.add_column(
        "vehicles",
        sa.Column("name", sa.VARCHAR(), autoincrement=False, nullable=False),
    )

    # Si on revient en arrière, on force vin + external_id en NOT NULL
    op.alter_column(
        "vehicles",
        "vin",
        existing_type=sa.VARCHAR(),
        nullable=False,
    )
    op.alter_column(
        "vehicles",
        "external_id",
        existing_type=sa.VARCHAR(),
        nullable=False,
    )

    op.drop_column("vehicles", "created_at")
    op.drop_column("vehicles", "nickname")

    op.create_index(
        op.f("ix_vehicle_status_timestamp"),
        "vehicle_status",
        ["timestamp"],
        unique=False,
    )

    op.alter_column(
        "vehicle_status",
        "is_plugged",
        existing_type=sa.BOOLEAN(),
        nullable=True,
    )
