# Copyright (c) 2026 Ilya Snegov (aka Sierra Arn)

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Originally from Backend Core
# https://github.com/Sierra-Arn/backend-core
# Modified for Full-Stack Core

# packages/shared/src/postgres_lib/models/user.py
from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base
from .types import Role, RoleSQL


class User(Base):
    """
    Represents a registered application user.

    Attributes
    ----------
    email : Mapped[str]
        Unique email address used for authentication and communication.
    hashed_password : Mapped[str]
        Bcrypt hash of the user password. The plaintext password is never
        stored or logged anywhere.
    role : Mapped[Role]
        Access level and permissions of the user. Determines which routes
        and actions are available. Default is USER for newly registered
        accounts. Elevation to higher roles must be performed by an
        administrator through the dedicated management interface.
    inference_runs_count : Mapped[int]
        Running total of model inference runs made by this user.
        Incremented by the Celery worker upon successful completion of
        each task. Used to enforce per-account inference quotas.
        Default is zero on registration.

    Notes
    -----
    The email attribute is declared with the unique parameter enabled,
    which causes PostgreSQL to automatically create a unique B-tree index
    on the column. This index serves two purposes. First, it enforces
    uniqueness by rejecting any insertion or update that would produce a
    duplicate address, guaranteeing each address belongs to exactly one
    account. Second, it accelerates login lookups. Every authentication
    attempt fetches the user record by email, and the B-tree index reduces
    each such lookup from a full table scan to logarithmic time complexity.
    """

    __tablename__ = "users"

    email: Mapped[str] = mapped_column(
        String(254),
        unique=True,
        nullable=False,
        index=True,
        comment="Unique email address; max 254 characters per RFC 5321",
    )
    hashed_password: Mapped[str] = mapped_column(
        String(60),
        nullable=False,
        comment="Bcrypt hash of the user password; bcrypt output is always exactly 60 characters",
    )
    role: Mapped[Role] = mapped_column(
        RoleSQL,
        nullable=False,
        default=Role.USER,
        server_default=Role.USER,
        comment="Access level and permissions of the user",
    )
    inference_runs_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
        comment="Total number of model inference runs made by this user",
    )