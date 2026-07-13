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

# packages/services/src/rate_limit_lib/service.py
import time
import uuid
from redis_lib.client import rate_limit_redis_client
from .config import rate_limit_config


class RateLimitService:
    """
    Stateless service for managing sliding window rate limit counters in Redis.

    All methods are classmethods that operate on the shared async Redis client
    directly. The sliding window is implemented as a sorted set where each
    member is a unique request identifier and each score is the Unix timestamp
    of the request.

    The identifier passed to each method determines the granularity of limiting:
    an IP address string is used for anonymous guests, and a prefixed account
    string such as user:42 is used for authenticated users, ensuring the two
    populations are counted independently.
    """

    @classmethod
    async def is_allowed(cls, identifier: str) -> bool:
        """
        Check whether the identifier is within the allowed request rate
        and record the current request if so.

        Parameters
        ----------
        identifier : str
            IP address for guest requests or a prefixed account string
            such as user:42 for authenticated requests.

        Returns
        -------
        bool
            True if the request is within the allowed rate and has been
            recorded. False if the limit has been reached and the request
            should be rejected.

        Notes
        -----
        The sliding window is implemented using two sequential pipelines.

        The first pipeline removes stale entries and reads the current count:
        ZREMRANGEBYSCORE drops all members with a timestamp older than
        now minus window_seconds, keeping only requests within the active
        window; ZCARD then returns the number of remaining members.

        If the count is below max_requests, the second pipeline records the
        request and resets the TTL: ZADD inserts the current timestamp as
        the score with a random UUID as the member to allow multiple requests
        at identical timestamps; EXPIRE resets the key lifetime to
        window_seconds so that idle keys are eventually removed automatically.

        Both pipelines use transaction=False because the commands within each
        pipeline are independent and do not require MULTI/EXEC semantics.

        This implementation is not fully atomic across both pipelines. Under
        extreme concurrency a small number of requests may slip through near
        the limit boundary. For strict atomicity a Lua script would be
        required. For most practical rate limiting use cases this trade-off
        is acceptable.
        """
        now = time.time()
        window_start = now - rate_limit_config.window_seconds

        async with rate_limit_redis_client.pipeline(transaction=False) as pipe:
            pipe.zremrangebyscore(identifier, "-inf", window_start)
            pipe.zcard(identifier)
            results = await pipe.execute()

        if results[1] >= rate_limit_config.max_requests:
            return False

        async with rate_limit_redis_client.pipeline(transaction=False) as pipe:
            pipe.zadd(identifier, {str(uuid.uuid4()): now})
            pipe.expire(identifier, rate_limit_config.window_seconds)
            await pipe.execute()

        return True