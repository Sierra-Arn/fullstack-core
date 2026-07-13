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

# packages/shared/src/postgres_lib/repositories/lead.py
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from .base import BaseRepository
from ..models import Lead, LeadStatus


class LeadRepository(BaseRepository):
    """
    Concrete repository for managing Lead entities in the database.

    Attributes
    ----------
    model_class : ClassVar[type[Lead]]
        Bound to the Lead ORM class at class definition time.
    """

    model_class = Lead

    @classmethod
    async def get_all(
        cls,
        session: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        status: LeadStatus | None = None,
    ) -> list[Lead]:
        """
        Fetch a paginated list of leads ordered by most recent first,
        with an optional filter by follow-up status.

        Parameters
        ----------
        session : AsyncSession
            Active async database session bound to the transaction.
        skip : int, optional
            Number of records to offset from the beginning of the
            result set. Default is 0.
        limit : int, optional
            Maximum number of records to return. Default is 100.
        status : LeadStatus or None, optional
            When provided, only leads matching this status are returned.
            When None, all leads are returned regardless of status.

        Returns
        -------
        list of Lead
            List of lead records ordered by created_at descending.
            Returns an empty list if no records match the given filters.
        """
        stmt = select(Lead).order_by(Lead.created_at.desc())

        if status is not None:
            stmt = stmt.where(Lead.status == status)

        stmt = stmt.offset(skip).limit(limit)
        result = await session.execute(stmt)
        return list(result.scalars().all())