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

# packages/server/src/server/shared/__init__.py
from .utils import html_response, create_icon, calculate_pagination
from .auth import role_for_display, role_for_authorization, get_session_user, require_role
from .parsing import parse_form, parse_query
from .schemas import EmailFieldMixin, PasswordFieldMixin, PageQuery
