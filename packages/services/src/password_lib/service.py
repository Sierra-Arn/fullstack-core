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

# packages/services/src/password_lib/service.py
import bcrypt
from .config import password_config


class PasswordService:
    """
    Stateless service for hashing and verifying passwords with bcrypt.

    All methods are classmethods and operate purely on the arguments
    passed to them, with no shared mutable state. The bcrypt cost factor
    is read from password_config at call time, so changes to the
    configuration are reflected immediately without restarting the process.
    """

    @classmethod
    def hash(cls, plaintext: str) -> str:
        """
        Hash a plaintext password with bcrypt.

        Parameters
        ----------
        plaintext : str
            Raw password string provided by the user. Never stored or
            logged anywhere after this call.

        Returns
        -------
        str
            Bcrypt hash of the password, always exactly 60 characters.
        """
        salt = bcrypt.gensalt(rounds=password_config.bcrypt_rounds)
        return bcrypt.hashpw(plaintext.encode(), salt).decode()

    @classmethod
    def verify(cls, plaintext: str, hashed: str) -> bool:
        """
        Verify a plaintext password against a stored bcrypt hash.

        Parameters
        ----------
        plaintext : str
            Raw password string provided by the user at login.
        hashed : str
            Bcrypt hash stored in the database for the account.

        Returns
        -------
        bool
            True if the plaintext matches the hash, False otherwise.
        """
        return bcrypt.checkpw(plaintext.encode(), hashed.encode())