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

# packages/server/src/server/modules/users/schemas.py
from dataclasses import dataclass
from postgres_lib import Role


@dataclass
class UserRoleForm:
    """
    Request shape for the user role update form.

    Normalizes the submitted role value on construction and exposes a
    parsed Role enum as a property. Handlers inspect that property and
    return a generic error when the value is not recognized.

    Attributes
    ----------
    role : str
        Target role value, stripped of surrounding whitespace. Default is
        empty string.
    """

    role: str = ""

    def __post_init__(self) -> None:
        """
        Normalize the submitted role field.
        """
        self.role = self.role.strip()

    @property
    def target_role(self) -> Role | None:
        """
        Return the parsed role enum value when recognized.

        Returns
        -------
        Role or None
            Parsed role when the submitted value maps to a known Role,
            otherwise None.
        """
        try:
            return Role(self.role)
        except ValueError:
            return None
