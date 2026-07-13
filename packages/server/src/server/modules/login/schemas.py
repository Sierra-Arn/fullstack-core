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

# packages/server/src/server/modules/login/schemas.py
from dataclasses import dataclass
from ...shared import EmailFieldMixin, PasswordFieldMixin


@dataclass
class LoginForm(EmailFieldMixin, PasswordFieldMixin):
    """
    Request shape for the login form.

    Composes shared email and password field mixins so submitted
    credentials are normalized on construction. The login handler returns
    a single generic error message on any failure and does not expose
    field-level validation.

    Attributes
    ----------
    email : str
        Email address, stripped and lowercased. Default is empty string.
    password : str
        Plaintext password, stripped of surrounding whitespace. Default is
        empty string.
    """

    def __post_init__(self) -> None:
        """
        Run normalization for all inherited field mixins.
        """
        super().__post_init__()
