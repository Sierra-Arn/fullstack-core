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

# packages/shared/src/postgres_lib/repositories/inference_history.py
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from .base import BaseRepository
from ..models import InferenceHistory


class InferenceHistoryRepository(BaseRepository):
    """
    Concrete repository for managing InferenceHistory entities in the database.

    Attributes
    ----------
    model_class : ClassVar[type[InferenceHistory]]
        Bound to the InferenceHistory ORM class at class definition time.
    """

    model_class = InferenceHistory

    @classmethod
    async def get_by_user_id(
        cls,
        session: AsyncSession,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> list[InferenceHistory]:
        """
        Fetch a paginated list of inference records for a specific user,
        ordered by most recent first.

        Parameters
        ----------
        session : AsyncSession
            Active async database session bound to the transaction.
        user_id : int
            Primary key of the user whose history is being fetched.
        skip : int, optional
            Number of records to offset from the beginning of the
            result set. Default is 0.
        limit : int, optional
            Maximum number of records to return. Default is 100.

        Returns
        -------
        list of InferenceHistory
            List of inference records belonging to the user, ordered
            by created_at descending. Returns an empty list if no
            records exist for the given user.
        """
        stmt = (
            select(InferenceHistory)
            .where(InferenceHistory.user_id == user_id)
            .order_by(InferenceHistory.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await session.execute(stmt)
        return list(result.scalars().all())
    
    @classmethod
    async def count_by_user_id(
        cls,
        session: AsyncSession,
        user_id: int,
    ) -> int:
        """
        Count inference history records for a specific user.
        
        Parameters
        ----------
        session : AsyncSession
            Active database session.
        user_id : int
            Primary key of the user whose records to count.
        
        Returns
        -------
        int
            Total number of inference records for the specified user.
        """
        result = await session.execute(
            select(func.count(InferenceHistory.id)).where(
                InferenceHistory.user_id == user_id
            )
        )
        return result.scalar_one()