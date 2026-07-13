"""Seed test data

Revision ID: fc8041e25d16
Revises: 0667fb39660d
Create Date: 2026-07-10 09:07:21.063101

"""
import os
import random
import secrets
from datetime import datetime, timezone, timedelta
from typing import Sequence, Union
import sqlalchemy as sa
from alembic import op
from dotenv import load_dotenv
from password_lib import PasswordService
from postgres_lib import LeadStatus

load_dotenv()

# revision identifiers, used by Alembic.
revision: str = 'fc8041e25d16'
down_revision: Union[str, Sequence[str], None] = '0667fb39660d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_LEAD_STATUSES = [status.value for status in LeadStatus]

_LOREM_IPSUM_SENTENCES = [
    "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
    "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
    "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris.",
    "Duis aute irure dolor in reprehenderit in voluptate velit esse cillum.",
    "Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia.",
    "Nemo enim ipsam voluptatem quia voluptas sit aspernatur aut odit aut fugit.",
    "Neque porro quisquam est, qui dolorem ipsum quia dolor sit amet.",
    "Quis autem vel eum iure reprehenderit qui in ea voluptate velit esse.",
    "At vero eos et accusamus et iusto odio dignissimos ducimus qui blanditiis.",
    "Nam libero tempore, cum soluta nobis est eligendi optio cumque nihil impedit.",
    "Temporibus autem quibusdam et aut officiis debitis aut rerum necessitatibus.",
    "Itaque earum rerum hic tenetur a sapiente delectus, ut aut reiciendis.",
    "Nulla facilisi etiam dignissim diam quis enim lobortis scelerisque fermentum.",
    "Pellentesque habitant morbi tristique senectus et netus et malesuada fames.",
    "Vivamus magna justo, lacinia eget consectetur sed, convallis at tellus.",
]


def _get_seed_config() -> dict[str, int]:
    """
    Read seed configuration from environment variables.

    Returns
    -------
    dict[str, int]
        Dictionary containing counts for each seed type with keys
        users_count, leads_count, and inference_history_count.

    Raises
    ------
    ValueError
        If any environment variable contains a negative value.
    """
    users_count = int(os.getenv("SEED_USERS_COUNT"))
    leads_count = int(os.getenv("SEED_LEADS_COUNT"))
    inference_history_count = int(os.getenv("SEED_INFERENCE_HISTORY_COUNT"))

    if users_count < 0:
        raise ValueError("SEED_USERS_COUNT must be non-negative.")
    if leads_count < 0:
        raise ValueError("SEED_LEADS_COUNT must be non-negative.")
    if inference_history_count < 0:
        raise ValueError("SEED_INFERENCE_HISTORY_COUNT must be non-negative.")

    return {
        "users_count": users_count,
        "leads_count": leads_count,
        "inference_history_count": inference_history_count,
    }


def _get_admin_user_id(bind: sa.engine.Connection) -> int:
    """
    Retrieve the admin user ID from the database.

    Parameters
    ----------
    bind : sqlalchemy.engine.Connection
        Active database connection.

    Returns
    -------
    int
        Primary key of the admin user.

    Raises
    ------
    ValueError
        If SEED_ADMIN_EMAIL is not set or no admin user exists.
    """
    admin_email = os.getenv("SEED_ADMIN_EMAIL")

    if not admin_email:
        raise ValueError(
            "SEED_ADMIN_EMAIL environment variable is required for admin seeding."
        )

    result = bind.execute(
        sa.text("SELECT id FROM users WHERE email = :email AND role = 'admin'"),
        {"email": admin_email},
    ).fetchone()

    if result is None:
        raise ValueError(
            f"Admin user with email {admin_email} not found. "
            "Run the admin seed migration first."
        )

    return result[0]


def _seed_users(bind: sa.engine.Connection, count: int) -> None:
    """
    Seed test user accounts.

    Parameters
    ----------
    bind : sqlalchemy.engine.Connection
        Active database connection.
    count : int
        Number of test users to create.
    """
    if count == 0:
        return

    now = datetime.now(timezone.utc)

    users = [
        {
            "email": f"testuser{i}@example.com",
            "hashed_password": PasswordService.hash(secrets.token_hex(16)),
            "role": "user",
            "inference_runs_count": random.randint(0, 10),
            "created_at": now,
        }
        for i in range(1, count + 1)
    ]

    bind.execute(
        sa.text(
            "INSERT INTO users (email, hashed_password, role, inference_runs_count, created_at) "
            "VALUES (:email, :hashed_password, :role, :inference_runs_count, :created_at)"
        ),
        users,
    )


def _seed_leads(bind: sa.engine.Connection, count: int) -> None:
    """
    Seed test collaboration request leads.

    Parameters
    ----------
    bind : sqlalchemy.engine.Connection
        Active database connection.
    count : int
        Number of test leads to create.
    """
    if count == 0:
        return

    now = datetime.now(timezone.utc)

    leads = [
        {
            "name": _LOREM_IPSUM_SENTENCES[i % len(_LOREM_IPSUM_SENTENCES)].split()[0:3],
            "email": f"lead{i}@example.com",
            "company": f"Company {i}" if i % 3 != 0 else None,
            "message": " ".join(
                _LOREM_IPSUM_SENTENCES[
                    j % len(_LOREM_IPSUM_SENTENCES)
                ]
                for j in range(i, i + 3)
            ),
            "status": _LEAD_STATUSES[i % len(_LEAD_STATUSES)],
            "created_at": now,
        }
        for i in range(1, count + 1)
    ]

    for lead in leads:
        lead["name"] = " ".join(lead["name"]).rstrip(",")

    bind.execute(
        sa.text(
            "INSERT INTO leads (name, email, company, message, status, created_at) "
            "VALUES (:name, :email, :company, :message, :status, :created_at)"
        ),
        leads,
    )


def _seed_inference_history(bind: sa.engine.Connection, admin_user_id: int, count: int) -> None:
    """
    Seed test inference history records for the admin user.

    Parameters
    ----------
    bind : sqlalchemy.engine.Connection
        Active database connection.
    admin_user_id : int
        Primary key of the admin user to associate records with.
    count : int
        Number of inference history records to create.
    """
    if count == 0:
        return

    now = datetime.now(timezone.utc)

    history_records = [
        {
            "input_text": " ".join(
                _LOREM_IPSUM_SENTENCES[
                    j % len(_LOREM_IPSUM_SENTENCES)
                ]
                for j in range(i, i + 2)
            ),
            "output_text": " ".join(
                _LOREM_IPSUM_SENTENCES[
                    j % len(_LOREM_IPSUM_SENTENCES)
                ]
                for j in range(i + 2, i + 5)
            ),
            "user_id": admin_user_id,
            "created_at": now - timedelta(days=random.randint(0, 30)),
        }
        for i in range(1, count + 1)
    ]

    bind.execute(
        sa.text(
            "INSERT INTO inference_history (input_text, output_text, user_id, created_at) "
            "VALUES (:input_text, :output_text, :user_id, :created_at)"
        ),
        history_records,
    )


def upgrade() -> None:
    """
    Seed test data for development and testing.

    Creates test users, collaboration request leads, and inference history
    records based on configuration from environment variables. The number
    of records for each type is controlled by SEED_USERS_COUNT,
    SEED_LEADS_COUNT, and SEED_INFERENCE_HISTORY_COUNT environment
    variables respectively. Inference history records are associated with
    the admin user identified by SEED_ADMIN_EMAIL.

    Raises
    ------
    ValueError
        If environment variables are invalid or admin user not found.
    """
    bind = op.get_bind()
    config = _get_seed_config()

    _seed_users(bind, config["users_count"])
    _seed_leads(bind, config["leads_count"])

    admin_user_id = _get_admin_user_id(bind)
    _seed_inference_history(bind, admin_user_id, config["inference_history_count"])


def downgrade() -> None:
    """
    Remove seeded test data.

    Deletes all test users, leads, and inference history records created
    by the upgrade migration. Test records are identified by their email
    patterns matching the testuser and lead prefixes.
    """
    bind = op.get_bind()

    bind.execute(
        sa.text("DELETE FROM users WHERE email LIKE 'testuser%@example.com'")
    )
    bind.execute(
        sa.text("DELETE FROM leads WHERE email LIKE 'lead%@example.com'")
    )
    bind.execute(
        sa.text(
            "DELETE FROM inference_history WHERE user_id IN "
            "(SELECT id FROM users WHERE email LIKE 'testuser%@example.com')"
        )
    )