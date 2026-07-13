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

# packages/server/src/server/modules/collaborate/schemas.py
from dataclasses import dataclass
from ...shared import EmailFieldMixin


@dataclass
class CollaborateForm(EmailFieldMixin):
    """
    Request shape for the collaboration request form.

    Composes the shared email field mixin and adds visitor-specific fields.
    Handlers inspect the inherited email check properties and the derived
    checks defined on this shape to choose user-facing error messages.

    Attributes
    ----------
    email : str
        Email address, stripped and lowercased. Default is empty string.
    name : str
        Visitor name, stripped of surrounding whitespace. Default is empty
        string.
    company : str
        Organization name, stripped of surrounding whitespace. Default is
        empty string.
    message : str
        Collaboration request description, stripped of surrounding
        whitespace. Default is empty string.
    """

    name: str = ""
    company: str = ""
    message: str = ""

    def __post_init__(self) -> None:
        """
        Run normalization for the inherited email mixin and local fields.
        """
        super().__post_init__()
        self.name = self.name.strip()
        self.company = self.company.strip()
        self.message = self.message.strip()

    @property
    def has_name(self) -> bool:
        """
        Return whether a visitor name was provided.

        Returns
        -------
        bool
            True when the name field is non-empty after normalization.
        """
        return bool(self.name)

    @property
    def has_message(self) -> bool:
        """
        Return whether a message was provided.

        Returns
        -------
        bool
            True when the message field is non-empty after normalization.
        """
        return bool(self.message)

    @property
    def optional_company(self) -> str | None:
        """
        Return the organization name or None when blank.

        Returns
        -------
        str or None
            Stripped organization name, or None when the field is empty
            after normalization.
        """
        return self.company or None
