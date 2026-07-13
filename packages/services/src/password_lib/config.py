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

# packages/services/src/password_lib/config.py
from typing import ClassVar, Final
from pydantic import Field
from base_lib import BaseConfig


class PasswordConfig(BaseConfig):
    """
    Configuration schema for password hashing.

    All fields support resolution from environment variables prefixed
    with PASSWORD_ following the BaseConfig precedence rules.

    Attributes
    ----------
    bcrypt_rounds : int
        Cost factor passed to bcrypt controlling how many rounds of
        hashing are performed. Higher values increase resistance to
        brute-force attacks at the cost of increased CPU time per
        hash. Must lie within the range supported by bcrypt (4–31).
        Default is 12.
    _algorithm : str
        Hashing algorithm used for all password operations. The bcrypt 
        package is the only hashing dependency installed in this project; 
        switching to a different algorithm would require adding the 
        corresponding library explicitly.
    """

    env_prefix: ClassVar[str] = "PASSWORD_"

    bcrypt_rounds: int = Field(default=12, ge=4, le=31)
    _algorithm: Final[str] = "bcrypt"


password_config = PasswordConfig()