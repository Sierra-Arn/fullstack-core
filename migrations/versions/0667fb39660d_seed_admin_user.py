"""Seed admin user

Revision ID: 0667fb39660d
Revises: b5dabad9f8b0
Create Date: 2026-07-10 09:03:01.602372

"""
import os
from datetime import datetime, timezone
from typing import Sequence, Union
import sqlalchemy as sa
from alembic import op
from dotenv import load_dotenv
from password_lib import PasswordService
from postgres_lib import Role, RoleSQL

load_dotenv()

# revision identifiers, used by Alembic.
revision: str = '0667fb39660d'
down_revision: Union[str, Sequence[str], None] = 'b5dabad9f8b0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Seed the initial administrator account.

    Creates the first admin user with credentials from environment variables.
    The admin role is set to 'admin' in the role enum column.

    Environment Variables
    ---------------------
    SEED_ADMIN_EMAIL : str
        Email address for the admin account.
    SEED_ADMIN_PASSWORD : str
        Plain text password that will be hashed before storage.

    Raises
    ------
    ValueError
        If required environment variables are not set.
    """
    admin_email = os.getenv("SEED_ADMIN_EMAIL")
    admin_password = os.getenv("SEED_ADMIN_PASSWORD")

    if not admin_email:
        raise ValueError(
            "SEED_ADMIN_EMAIL environment variable is required for admin seeding."
        )

    if not admin_password:
        raise ValueError(
            "SEED_ADMIN_PASSWORD environment variable is required for admin seeding."
        )

    now = datetime.now(timezone.utc)
    hashed_password = PasswordService.hash(admin_password)

    bind = op.get_bind()
    
    users_table = sa.table(
        "users",
        sa.column("email", sa.String),
        sa.column("hashed_password", sa.String),
        sa.column("role", RoleSQL),
        sa.column("inference_runs_count", sa.Integer),
        sa.column("created_at", sa.DateTime(timezone=True)),
    )
    
    bind.execute(
        users_table.insert().values(
            email=admin_email,
            hashed_password=hashed_password,
            role=Role.ADMIN,
            inference_runs_count=0,
            created_at=now,
        )
    )


def downgrade() -> None:
    """
    Remove the seeded administrator account.

    Deletes the admin user created by the upgrade migration using the
    email address from the environment variable.

    Environment Variables
    ---------------------
    SEED_ADMIN_EMAIL : str
        Email address of the admin account to remove.

    Raises
    ------
    ValueError
        If SEED_ADMIN_EMAIL environment variable is not set.
    """
    admin_email = os.getenv("SEED_ADMIN_EMAIL")

    if not admin_email:
        raise ValueError(
            "SEED_ADMIN_EMAIL environment variable is required for admin removal."
        )

    bind = op.get_bind()
    bind.execute(
        sa.text("DELETE FROM users WHERE email = :email"),
        {"email": admin_email},
    )