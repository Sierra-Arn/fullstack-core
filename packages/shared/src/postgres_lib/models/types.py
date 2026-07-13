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

# packages/shared/src/postgres_lib/models/types.py
from enum import StrEnum
from sqlalchemy import Enum as SQLEnum


class LeadStatus(StrEnum):
    """
    Follow-up state of a submitted collaboration request.

    Attributes
    ----------
    NEW : LeadStatus
        Just submitted; no administrator has acted on it yet.
    IN_PROGRESS : LeadStatus
        An administrator has picked up the request and is actively
        handling it.
    ANSWERED : LeadStatus
        The administrator has responded and the request is resolved
        successfully.
    REJECTED : LeadStatus
        The request was reviewed and declined by an administrator.
    """

    NEW = "new"
    IN_PROGRESS = "in_progress"
    ANSWERED = "answered"
    REJECTED = "rejected"


LeadStatusSQL = SQLEnum(
    *[e.value for e in LeadStatus],
    name="lead_status",
)
"""
SQLAlchemy column type mapping LeadStatus to a named PostgreSQL enum.

Restricts the column at the database level to the predefined set of states,
keeping data integrity independent of application-layer validation. The named
type appears explicitly in migrations, which improves their readability.
"""


class Role(StrEnum):
    """
    Access level and permissions of a user in the system.

    Attributes
    ----------
    UNAUTHENTICATED : Role
        Unregistered visitor. Can only perform login or registration
        actions.
    USER : Role
        Authenticated regular user. Inherits unauthenticated permissions
        and can additionally perform model inference.
    MODERATOR : Role
        Trusted user with elevated privileges. Inherits user permissions
        and can additionally read collaboration leads submitted by other
        users.
    ADMIN : Role
        System administrator with full control. Inherits moderator
        permissions and can additionally manage user accounts, including
        changing roles and deleting accounts from the database.
    """

    UNAUTHENTICATED = "unauthenticated"
    USER = "user"
    MODERATOR = "moderator"
    ADMIN = "admin"

    @property
    def level(self) -> int:
        """
        Numeric privilege level for hierarchical access control.

        Higher values indicate greater permissions. Used to determine
        if a user role satisfies the minimum required role for a
        specific action or route.

        Returns
        -------
        int
            Integer representing the privilege weight of the role.
        """
        return {
            "unauthenticated": 0,
            "user": 1,
            "moderator": 2,
            "admin": 3,
        }[self.value]


RoleSQL = SQLEnum(
    *[e.value for e in Role],
    name="role",
)
"""
SQLAlchemy column type mapping Role to a named PostgreSQL enum.

Restricts the column at the database level to the predefined set of roles,
keeping data integrity independent of application-layer validation. The named
type appears explicitly in migrations, which improves their readability.
"""