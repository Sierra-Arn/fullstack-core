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

# packages/server/src/server/modules/landing/routes.py
from fasthtml.common import FT
from starlette.requests import Request
from postgres_lib import Role
from .pages import create_landing_page
from ...shared import role_for_display


@role_for_display
async def landing_get(request: Request, role: Role) -> FT:
    """
    Render the public landing page.

    The decorator automatically extracts the current user role from the
    session and injects it into this handler. The role is used purely
    for display purposes to conditionally render UI elements such as
    navigation links and call-to-action buttons. The page remains
    accessible to all visitors regardless of authentication state.

    Parameters
    ----------
    request : Request
        Incoming HTTP request.
    role : Role
        Current user access role, automatically extracted from the
        session by the role_for_display decorator.

    Returns
    -------
    FT
        FastHTML element representing the complete landing page.
    """
    return create_landing_page(role=role)