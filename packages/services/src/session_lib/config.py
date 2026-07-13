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

# packages/services/src/session_lib/config.py
from typing import ClassVar
from pydantic import Field
from base_lib import BaseConfig


class SessionConfig(BaseConfig):
    """
    Configuration schema for server-side session management.

    All fields support resolution from environment variables prefixed
    with SESSION_ following the BaseConfig precedence rules.

    Attributes
    ----------
    ttl_seconds : int
        Lifetime of a session entry in Redis in seconds. The TTL is
        reset on every authenticated request so that active users are
        not logged out mid-session. Default is 86400 (24 hours).
    session_id_length : int
        Number of random bytes used to generate the opaque session
        identifier via secrets.token_hex. The resulting hex string is
        twice this length. Default is 32, producing a 64-character
        identifier.
    cookie_name : str
        Name of the HTTP cookie that carries the session identifier.
        Default is "session_id".
    cookie_path : str
        URL path scope for which the session cookie is sent by the
        browser. When set to the root path, the cookie is included
        in requests to all application routes. Must match the path
        used when the cookie was originally set, otherwise the browser
        will not delete it on logout. Default is "/".
    cookie_httponly : bool
        Whether the session cookie is inaccessible to JavaScript. When
        True, the cookie cannot be read by client-side scripts, providing
        protection against cross-site scripting attacks. Default is True.
    cookie_samesite : str
        SameSite attribute controlling when the session cookie is sent
        with cross-site requests. Valid values are "strict", "lax", and
        "none". The "lax" setting provides a balance between security
        and usability by allowing the cookie to be sent with top-level
        navigations while blocking it in most cross-site contexts.
        Default is "lax".
    cookie_secure : bool
        Whether the session cookie is transmitted only over HTTPS. When
        True, the cookie is never sent with unencrypted HTTP requests,
        protecting it from interception on insecure networks. Should be
        set to True in production environments. Default is True.
    """

    env_prefix: ClassVar[str] = "SESSION_"

    ttl_seconds: int = Field(default=86400, ge=1)
    session_id_length: int = Field(default=32, ge=16)
    cookie_name: str = "session_id"
    cookie_path: str = "/"
    cookie_httponly: bool = True
    cookie_samesite: str = "lax"
    cookie_secure: bool = True


session_config = SessionConfig()