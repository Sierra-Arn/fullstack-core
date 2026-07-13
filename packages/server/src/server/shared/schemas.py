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

# packages/server/src/server/shared/schemas.py
from dataclasses import dataclass
from ..config import server_config


class _RequestShape:
    """
    Cooperative base class for request shape mixins.

    Provides an empty __post_init__ hook so mixin classes can call
    super().__post_init__() and chain normalization across multiple
    inherited field mixins without reaching object.
    """

    def __post_init__(self) -> None:
        """
        No-op hook for cooperative mixin chaining.
        """
        pass


@dataclass
class EmailFieldMixin(_RequestShape):
    """
    Reusable email field with normalization and derived checks.

    Strips surrounding whitespace, converts the address to lowercase,
    and exposes non-empty and format checks as properties. Handlers
    inspect those properties and choose the user-facing error message
    to return.

    Attributes
    ----------
    email : str
        Email address, stripped and lowercased. Default is empty string.
    """

    email: str = ""

    def __post_init__(self) -> None:
        """
        Normalize the email field and continue the mixin chain.
        """
        self.email = self.email.strip().lower()
        super().__post_init__()

    @property
    def has_email(self) -> bool:
        """
        Return whether an email address was provided.

        Returns
        -------
        bool
            True when the email field is non-empty after normalization.
        """
        return bool(self.email)

    @property
    def email_is_valid(self) -> bool:
        """
        Return whether the email address matches the expected format.

        Returns
        -------
        bool
            True when the email field is a well-formed address.
        """
        return bool(server_config._email_pattern.match(self.email))


@dataclass
class PasswordFieldMixin(_RequestShape):
    """
    Reusable password field with normalization and a non-empty check.

    Strips surrounding whitespace and exposes a non-empty check as a
    property. Handlers inspect that property and choose the user-facing
    error message to return.

    Attributes
    ----------
    password : str
        Plaintext password, stripped of surrounding whitespace. Default is
        empty string.
    """

    password: str = ""

    def __post_init__(self) -> None:
        """
        Normalize the password field and continue the mixin chain.
        """
        self.password = self.password.strip()
        super().__post_init__()

    @property
    def has_password(self) -> bool:
        """
        Return whether a password was provided.

        Returns
        -------
        bool
            True when the password field is non-empty after normalization.
        """
        return bool(self.password)


@dataclass
class PageQuery:
    """
    Shared request shape for paginated list endpoints.

    Describes the single page query parameter shared by every paginated
    endpoint. The raw string is captured as submitted, and the number
    property exposes a sanitized one-based page number so handlers never
    parse the value themselves. The upper bound is enforced separately
    against the actual record count during pagination.

    Attributes
    ----------
    page : str
        Raw one-based page number from the query string. Default is "1"
        when the parameter is absent.
    """

    page: str = "1"

    @property
    def number(self) -> int:
        """
        Return the sanitized one-based page number.

        Any missing, non-numeric, or below-range value falls back to the
        first page. The upper bound is not applied here because it depends
        on the total record count known only at query time.

        Returns
        -------
        int
            A page number of at least 1.
        """
        try:
            page = int(self.page)
        except (TypeError, ValueError):
            return 1

        return max(1, page)
