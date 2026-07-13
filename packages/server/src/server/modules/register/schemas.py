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

# packages/server/src/server/modules/register/schemas.py
from dataclasses import dataclass
from ...shared import EmailFieldMixin, PasswordFieldMixin


@dataclass
class RegisterForm(EmailFieldMixin, PasswordFieldMixin):
    """
    Request shape for the registration form.

    Composes shared email and password field mixins and adds a password
    confirmation field. Handlers inspect the inherited check properties
    and the passwords_match property to choose user-facing error messages.

    Attributes
    ----------
    email : str
        Email address, stripped and lowercased. Default is empty string.
    password : str
        Plaintext password, stripped of surrounding whitespace. Default is
        empty string.
    confirm_password : str
        Password confirmation, stripped of surrounding whitespace.
        Default is empty string.
    """

    confirm_password: str = ""

    def __post_init__(self) -> None:
        """
        Run normalization for all inherited field mixins and the
        confirmation field.
        """
        super().__post_init__()
        self.confirm_password = self.confirm_password.strip()

    @property
    def passwords_match(self) -> bool:
        """
        Return whether the password and confirmation fields match.

        Returns
        -------
        bool
            True when both password fields are identical after
            normalization.
        """
        return self.password == self.confirm_password
