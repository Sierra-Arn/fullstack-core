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

# packages/services/src/session_lib/service.py
import secrets
from redis_lib import session_redis_client
from .config import session_config
from .types import SessionPayload


class SessionService:
    """
    Stateless service for managing server-side sessions in Redis.

    Each session is stored as a Redis hash under a key derived from the
    session identifier. The session payload is a structured object
    containing the authenticated user id and their access role.

    All methods are classmethods that operate on the shared async Redis
    client directly.
    """

    @classmethod
    def _generate_session_id(cls) -> str:
        """
        Generate a cryptographically secure opaque session identifier.

        Returns
        -------
        str
            Hex string of length session_id_length * 2 produced by
            secrets.token_hex.
        """
        return secrets.token_hex(session_config.session_id_length)

    @classmethod
    async def create(cls, payload: SessionPayload) -> str:
        """
        Create a new session and persist it to Redis.

        Parameters
        ----------
        payload : SessionPayload
            Session data to store. Complex types like enums are
            automatically serialized to strings for Redis storage.

        Returns
        -------
        str
            Newly generated session identifier to be set as a cookie
            on the client.
        """
        session_id = cls._generate_session_id()
        mapping = {k: str(v) for k, v in payload.model_dump().items()}

        async with session_redis_client.pipeline(transaction=True) as pipe:
            pipe.hset(session_id, mapping=mapping)
            pipe.expire(session_id, session_config.ttl_seconds)
            await pipe.execute()

        return session_id

    @classmethod
    async def get(cls, session_id: str) -> SessionPayload | None:
        """
        Fetch session data and refresh its TTL.

        Parameters
        ----------
        session_id : str
            Opaque session identifier read from the request cookie.

        Returns
        -------
        SessionPayload or None
            Parsed session payload, or None if the session does not
            exist or has expired.
        """
        async with session_redis_client.pipeline(transaction=True) as pipe:
            pipe.hgetall(session_id)
            pipe.expire(session_id, session_config.ttl_seconds)
            results = await pipe.execute()

        raw_payload = results[0]
        if not raw_payload:
            return None
            
        return SessionPayload.model_validate(raw_payload)

    @classmethod
    async def delete(cls, session_id: str) -> None:
        """
        Delete a session from Redis, effectively logging the user out.

        Parameters
        ----------
        session_id : str
            Opaque session identifier read from the request cookie.
        """
        await session_redis_client.delete(session_id)