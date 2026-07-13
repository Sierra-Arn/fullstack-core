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

# packages/server/src/server/modules/inference/schemas.py
from dataclasses import dataclass


@dataclass
class InferenceForm:
    """
    Request shape for the inference form.

    Normalizes the submitted prompt on construction and exposes a derived
    non-empty check as a property. Handlers inspect that property and
    choose the user-facing error message to return.

    Attributes
    ----------
    input_text : str
        Model prompt text, stripped of surrounding whitespace. Default is
        empty string.
    """

    input_text: str = ""

    def __post_init__(self) -> None:
        """
        Normalize the submitted prompt field.
        """
        self.input_text = self.input_text.strip()

    @property
    def has_input(self) -> bool:
        """
        Return whether a prompt was provided.

        Returns
        -------
        bool
            True when the input_text field is non-empty after
            normalization.
        """
        return bool(self.input_text)
