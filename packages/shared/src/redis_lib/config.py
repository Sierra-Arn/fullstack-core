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

# packages/shared/src/redis_lib/config.py
from typing import ClassVar
from pydantic import Field
from base_lib import BaseConfig


class RedisConfig(BaseConfig):
    """
    Configuration schema for Redis service connectivity.

    Stores connection parameters for accessing a Redis instance. All fields
    support resolution from environment variables prefixed with REDIS_ following
    the BaseConfig precedence rules. Each logical concern (sessions, rate
    limiting, Celery broker, and Celery result backend) is isolated to its
    own Redis database, allowing independent flushing and monitoring.

    Attributes
    ----------
    host : str
        Hostname or IP address of the Redis server endpoint.
        Default is "127.0.0.1".
    port : int
        TCP port for the Redis service; validated to lie within the standard
        16-bit range. Default is 6379.
    user_name : str
        Username for Redis ACL-based authentication.
    user_password : str
        Password for Redis authentication; treated as sensitive data.
    session_db_index : int
        Redis database number used for server-side session storage.
        Default is 0.
    rate_limit_db_index : int
        Redis database number used for rate limiting counters.
        Default is 1.
    broker_db_index : int
        Redis database number used by Celery as the task broker.
        Default is 2.
    result_backend_db_index : int
        Redis database number used by Celery to store task results.
        Default is 3.
    session_url : str
        Read-only property assembling the Redis connection URI for
        session storage.
    rate_limit_url : str
        Read-only property assembling the Redis connection URI for
        rate limiting counters.
    broker_url : str
        Read-only property assembling the Redis connection URI for the
        Celery task broker.
    result_backend_url : str
        Read-only property assembling the Redis connection URI for the
        Celery result backend.
    """

    env_prefix: ClassVar[str] = "REDIS_"

    host: str = "127.0.0.1"
    port: int = Field(default=6379, ge=1, le=65535)
    user_name: str
    user_password: str
    session_db_index: int = Field(default=0, ge=0)
    rate_limit_db_index: int = Field(default=1, ge=0)
    broker_db_index: int = Field(default=2, ge=0)
    result_backend_db_index: int = Field(default=3, ge=0)

    def _build_url(self, db: int) -> str:
        """
        Assemble a Redis connection URI for the given database index.

        Parameters
        ----------
        db : int
            Redis database number to include as the URI path component.

        Returns
        -------
        str
            Complete Redis connection URI in the format
            redis://username:password@host:port/db.
        """
        return (
            f"redis://{self.user_name}:"
            f"{self.user_password}@"
            f"{self.host}:{self.port}/"
            f"{db}"
        )

    @property
    def session_url(self) -> str:
        """
        Build Redis connection URL for session storage.

        Returns
        -------
        str
            Redis URI pointing to session_db_index.
        """
        return self._build_url(self.session_db_index)

    @property
    def rate_limit_url(self) -> str:
        """
        Build Redis connection URL for rate limiting counters.

        Returns
        -------
        str
            Redis URI pointing to rate_limit_db_index.
        """
        return self._build_url(self.rate_limit_db_index)

    @property
    def broker_url(self) -> str:
        """
        Build Redis connection URL for the Celery task broker.

        Returns
        -------
        str
            Redis URI pointing to broker_db_index.
        """
        return self._build_url(self.broker_db_index)

    @property
    def result_backend_url(self) -> str:
        """
        Build Redis connection URL for the Celery result backend.

        Returns
        -------
        str
            Redis URI pointing to result_backend_db_index.
        """
        return self._build_url(self.result_backend_db_index)


redis_config = RedisConfig()