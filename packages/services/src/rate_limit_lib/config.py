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

# packages/services/src/rate_limit_lib/config.py
from typing import ClassVar
from pydantic import Field
from base_lib import BaseConfig


class RateLimitConfig(BaseConfig):
    """
    Configuration schema for sliding window rate limiting.

    Controls how aggressively incoming requests are throttled before any
    route logic executes. All fields support resolution from environment
    variables prefixed with RATE_LIMIT_ following the BaseConfig precedence
    rules.

    Attributes
    ----------
    max_requests : int
        Maximum number of requests a single identifier may make within
        one window. Applies to both IP-keyed guest requests and
        account-keyed authenticated requests. Default is 100.
    window_seconds : int
        Duration of the sliding window in seconds. Requests older than
        this threshold are evicted from the counter and no longer count
        toward the limit. Default is 60.
    """

    env_prefix: ClassVar[str] = "RATE_LIMIT_"

    max_requests: int = Field(default=100, ge=1)
    window_seconds: int = Field(default=60, ge=1)


rate_limit_config = RateLimitConfig()