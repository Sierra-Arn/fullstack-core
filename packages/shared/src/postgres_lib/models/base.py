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

# packages/shared/src/postgres_lib/models/base.py
from datetime import datetime
from sqlalchemy import Integer, DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """
    Central registry for all ORM models in the application.

    Every class that inherits from Base is automatically registered in
    Base.metadata, a collection of all Table objects in the schema.
    Without a shared Base, SQLAlchemy has no way to know which classes
    are models, so ORM features like relationship and automatic
    Python-object mapping would not work.
 
    Inheritance also provides a surrogate integer primary key and an
    immutable creation timestamp shared uniformly across all models.

    Attributes
    ----------
    id : Mapped[int]
        Surrogate primary key for the record. Automatically assigned
        as a monotonically increasing integer upon insertion.
    created_at : Mapped[datetime]
        Timezone-aware timestamp indicating when the record was first inserted.
        Set automatically by the database using the current UTC time at insert
        time. Value remains immutable after creation.
    """

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="Primary key identifier",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        comment="Record creation timestamp",
    )
