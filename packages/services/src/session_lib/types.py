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

# packages/services/src/session_lib/types.py
from pydantic import BaseModel, model_validator
from postgres_lib import Role


class SessionPayload(BaseModel):
    """
    Structured payload for server-side sessions.

    Encapsulates session data and handles automatic serialization
    and deserialization of complex types like StrEnum when
    interacting with Redis. For unauthenticated visitors, the user
    identifier is null and the role is strictly set to unauthenticated.

    Attributes
    ----------
    user_id : int or None
        Unique identifier of the authenticated user. Null for
        unauthenticated visitors.
    role : Role
        Access level and permissions of the user.
    """

    user_id: int | None
    role: Role

    @model_validator(mode="after")
    def _validate_auth_consistency(self) -> "SessionPayload":
        """
        Ensure authentication state and role are strictly consistent.

        An unauthenticated session must have a null user identifier
        and the unauthenticated role. Conversely, a null user
        identifier implies the unauthenticated role.

        Returns
        -------
        SessionPayload
            The validated instance.

        Raises
        ------
        ValueError
            If the user identifier and role contradict each other.
        """
        if self.role == Role.UNAUTHENTICATED and self.user_id is not None:
            raise ValueError(
                "Unauthenticated sessions cannot have a user identifier."
            )
        
        if self.user_id is None and self.role != Role.UNAUTHENTICATED:
            raise ValueError(
                "Sessions without a user identifier must have the unauthenticated role."
            )
            
        return self