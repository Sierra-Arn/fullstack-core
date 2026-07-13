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

# packages/shared/src/redis_lib/client.py
import redis.asyncio as aioredis
from .config import redis_config


session_redis_client = aioredis.from_url(
    redis_config.session_url,
    decode_responses=True,
)
"""
Asynchronous Redis client for server-side session storage.
Connects to the session database defined by session_db_index.
"""

rate_limit_redis_client = aioredis.from_url(
    redis_config.rate_limit_url,
    decode_responses=True,
)
"""
Asynchronous Redis client for sliding window rate limit counters.
Connects to the rate limiting database defined by rate_limit_db_index.
"""