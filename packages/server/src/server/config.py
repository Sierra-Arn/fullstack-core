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

# packages/server/src/server/config.py
import re
from enum import StrEnum
from typing import ClassVar, Final
from pydantic import Field
from base_lib import BaseConfig, LogLevel


class RoutePath(StrEnum):
    """
    Centralized URL path constants for the application.

    All route paths are defined here to avoid magic strings scattered
    throughout the codebase. This provides a single source of truth
    for URL construction and makes refactoring safer.

    Paths containing placeholders such as {id} or {task_id} must be
    formatted with the appropriate values before use in actual HTTP
    requests or HTMX attributes.

    Attributes
    ----------
    LANDING : RoutePath
        Landing page accessible to all visitors.
    LOGIN : RoutePath
        Authentication form for existing users.
    REGISTER : RoutePath
        Registration form for new users.
    COLLABORATE : RoutePath
        Collaboration request form accessible to all visitors.
    LOGOUT : RoutePath
        Session termination endpoint.
    INFERENCE : RoutePath
        Model inference interface for authenticated users.
    INFERENCE_HISTORY : RoutePath
        Paginated history of completed inference runs.
    LEADS : RoutePath
        Collaboration requests management page. Accessible to users
        with MODERATOR or ADMIN role.
    USERS : RoutePath
        User accounts management page. Accessible only to users
        with ADMIN role.
    INFERENCE_STATUS : RoutePath
        Celery task status polling endpoint with {task_id} placeholder.
    LEAD_STATUS : RoutePath
        Lead status transition endpoint with {id} placeholder.
        Accessible to users with MODERATOR or ADMIN role.
    USER_ROLE : RoutePath
        User role assignment endpoint with {id} placeholder. Accepts
        a target role value and updates the user record accordingly.
        Accessible only to users with ADMIN role.
    USER_DELETE : RoutePath
        User account deletion endpoint with {id} placeholder.
        Accessible only to users with ADMIN role.
    HEALTH_SHALLOW : RoutePath
        Lightweight health check verifying basic service availability.
    HEALTH_DEEP : RoutePath
        Comprehensive health check probing all external dependencies.
    """

    # ===== PUBLIC ROUTES =====
    LANDING = "/"
    LOGIN = "/login"
    REGISTER = "/register"
    COLLABORATE = "/collaborate"
    LOGOUT = "/logout"

    # ===== AUTHENTICATED USER ROUTES =====
    INFERENCE = "/inference"
    INFERENCE_HISTORY = "/inference/history"

    # ===== MODERATOR AND ADMIN ROUTES =====
    LEADS = "/leads"

    # ===== ADMIN ONLY ROUTES =====
    USERS = "/users"

    # ===== PARAMETERIZED ENDPOINTS =====
    INFERENCE_STATUS = "/inference/status/{task_id}"
    LEAD_STATUS = "/leads/{id}/status"
    USER_ROLE = "/users/{id}/role"
    USER_DELETE = "/users/{id}/delete"

    # ===== HEALTH CHECKS =====
    HEALTH_SHALLOW = "/health/shallow"
    HEALTH_DEEP = "/health/deep"


class ServerConfig(BaseConfig):
    """
    Configuration schema for the FastHTML server runtime.

    Stores server binding parameters, logging thresholds, and application
    behaviour limits. All fields support resolution from environment variables
    prefixed with SERVER_ following the BaseConfig precedence rules.

    Attributes
    ----------
    host : str
        Network interface address for the server to bind. Use "0.0.0.0"
        to accept connections from any interface or "127.0.0.1" for
        localhost only. Default is "0.0.0.0".
    port : int
        TCP port for incoming HTTP requests. Validated to lie within the
        standard 16-bit range. Default is 8000.
    log_level : LogLevel
        Minimum severity threshold for all server-process logs.
        Default is "INFO".
    app_name: str
        Human-readable application name rendered in the navbar brand link and
        the HTML title element of every page. Default is "Full-stack Core".
    ui_theme: str
        DaisyUI theme applied to the root HTML element via the data-theme attribute.
        Any theme from the DaisyUI theme catalogue is valid (e.g. light, dark,
        corporate, cupcake). Default is "light".
    github_url : str
        GitHub profile URL of the project author, linked in the footer
        social section. Exposed via environment variable so the same
        codebase can be deployed under different author identities without
        code changes. Default is "https://github.com/Sierra-Arn".
    privacy_policy_url : str
        URL of the platform privacy policy document linked in the footer.
        Informs users about what data is collected during model inference
        sessions, how session identifiers and hashed credentials are stored,
        and the data retention policy for inference history records.
        Default is "https://www.youtube.com/watch?v=dQw4w9WgXcQ".
    inference_quota : int
        Maximum number of model inference runs permitted per authenticated
        user account. Checked against users.inference_runs_count before
        enqueuing a task; requests that would exceed this threshold are
        rejected with a 429 response before any work is dispatched.
        Default is 3.
    page_size : int
        Default number of records per page for paginated views throughout
        the application. Applied uniformly across all user roles. 
        Default is 10.
    deep_health_timeout : float
        Maximum time in seconds allowed for the deep health check to
        complete all dependency probes before returning unavailable.
        Controls the deadline applied to concurrent database, cache,
        and broker checks. Default is 3.0.
    _session_class : None
        Session handler class passed to the FastHTML application constructor.
        Set to None because the application implements a custom server-side
        session management layer backed by Redis, making the built-in
        Starlette session middleware unnecessary. Fixed and not configurable
        via environment.
    _surreal_enabled : bool
        Flag controlling whether Surreal.js is automatically included in
        the application head. Set to False because the application uses
        Alpine.js for client-side reactivity instead of Surreal.js.
        Fixed and not configurable via environment.
    _htmx_enabled : bool
        Flag controlling whether HTMX is automatically included via
        FastHTML default headers. Set to False because HTMX is bundled
        manually through the build-js pipeline together with Alpine.js,
        providing version control and tree-shaking capabilities. Fixed
        and not configurable via environment.
    _default_headers_enabled : bool
        Flag controlling whether FastHTML injects its standard set of
        HTTP headers and meta tags into every response. Set to False
        because the application manages headers explicitly through the
        shared layout component to maintain full control over security
        headers, viewport configuration, and metadata. Fixed and not
        configurable via environment.
    _email_pattern : re.Pattern
        Compiled regular expression used to validate email address format
        in request shapes. Fixed and not configurable via environment.
    """

    env_prefix: ClassVar[str] = "SERVER_"

    # ===== ENV-DEPENDENT (configurable via SERVER_ prefixed env vars) =====
    host: str = "0.0.0.0"
    port: int = Field(default=8000, ge=1, le=65535)
    log_level: LogLevel = "INFO"
    app_name: str = "Full-stack Core"
    ui_theme: str = "light"
    github_url : str = "https://github.com/Sierra-Arn"
    privacy_policy_url : str = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    inference_quota: int = Field(default=3, ge=1)
    page_size: int = Field(default=10, ge=1)
    deep_health_timeout: float = Field(default=3.0, gt=0)

    # ====== ARCHITECTURAL CONSTANTS (private, not configurable via env) ======
    _session_class: Final[None] = None
    _surreal_enabled: Final[bool] = False
    _htmx_enabled: Final[bool] = False
    _default_headers_enabled: Final[bool] = False
    _email_pattern: Final[re.Pattern[str]] = re.compile(
        r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
    )


server_config = ServerConfig()