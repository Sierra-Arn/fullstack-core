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

# packages/shared/src/postgres_lib/models/lead.py
from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base
from .types import LeadStatus, LeadStatusSQL


class Lead(Base):
    """
    Represents a collaboration request submitted by a visitor.

    Attributes
    ----------
    name : Mapped[str]
        Name provided by the visitor for follow-up communication.
    email : Mapped[str]
        Contact email provided by the visitor. Not unique, as the same
        person may legitimately submit multiple requests.
    company : Mapped[str | None]
        Optional organization name. None when the visitor leaves the
        field blank.
    message : Mapped[str]
        Free-form description of the intended use case or project
        requirements.
    status : Mapped[LeadStatus]
        Current follow-up state of the request. Default is NEW upon
        submission and is advanced by an administrator.
    """

    __tablename__ = "leads"

    name: Mapped[str] = mapped_column(
        String(120),
        nullable=False,
        comment="Full name provided by the visitor for follow-up communication",
    )
    email: Mapped[str] = mapped_column(
        String(254),
        nullable=False,
        comment="Contact email address; max 254 characters per RFC 5321; not unique to allow repeat enquiries",
    )
    message: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Free-form text describing the intended use case or project requirements",
    )
    company: Mapped[str | None] = mapped_column(
        String(120),
        nullable=True,
        default=None,
        comment="Optional organization or company name",
    )
    status: Mapped[LeadStatus] = mapped_column(
        LeadStatusSQL,
        nullable=False,
        default=LeadStatus.NEW,
        server_default=LeadStatus.NEW.value,
        comment="Current follow-up state of the collaboration request",
    )