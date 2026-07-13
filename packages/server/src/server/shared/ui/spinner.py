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

# packages/server/src/server/shared/ui/spinner.py
from fasthtml.common import Div, Span, FT


def create_spinner(
    message: str | None = "Processing your request...",
) -> FT:
    """
    Create a visual loading indicator to provide feedback during
    asynchronous operations.

    Parameters
    ----------
    message : str or None
        Optional textual status message displayed below the spinner.
        If None, only the spinner animation is rendered. Default is
        "Processing your request...".

    Returns
    -------
    FT
        Fully assembled FastHTML container element representing the
        loading state, including accessibility attributes for screen
        readers.
    """
    content: list[FT] = [
        Span(
            cls="loading loading-spinner loading-lg text-primary",
        )
    ]

    if message:
        content.append(
            Div(
                message,
                cls="text-base-content/60 text-sm mt-4",
            )
        )

    return Div(
        Div(
            *content,
            cls="flex flex-col items-center gap-2",
        ),
        cls="flex justify-center items-center py-12",
        role="status",
        aria_live="polite",
    )