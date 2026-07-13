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

# Originally from Human Pose Estimation Service
# https://github.com/Sierra-Arn/pose-estimation-service
# Modified for Full-Stack Core

# packages/shared/src/postgres_lib/__init__.py
from .config import postgres_config
from .session import (
    sync_engine, sync_session_factory, get_sync_db_session,
    async_engine, async_session_factory, get_async_db_session
)
from .models import (
    Base, User, InferenceHistory, Lead, 
    LeadStatus, LeadStatusSQL, Role, RoleSQL
)
from .repositories import (
    BaseRepository, UserRepository, 
    InferenceHistoryRepository, LeadRepository
)