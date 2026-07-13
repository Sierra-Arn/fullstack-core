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

# packages/server/src/server/shared/ui/empty_state.py
from fasthtml.common import Div, P, FT
from ..utils import create_icon


def create_empty_state(
    message: str,
    *,
    icon_name: str | None = None,
) -> Div:
    """
    Create an empty state placeholder for paginated lists.

    Displayed when a query returns no records, providing a neutral
    placeholder instead of an empty list. The message is centered
    and styled as subtle informational text.

    Parameters
    ----------
    message : str
        Human-readable text explaining that no records are available.
    icon_name : str or None
        Optional Heroicon name to display above the message for
        visual context. When None, only the text is rendered.
        Default is None.

    Returns
    -------
    Div
        FastHTML container holding the empty state message and
        optional icon, centered and styled as subtle informational text.
    """
    children: list[FT] = []

    if icon_name:
        children.append(
            create_icon(icon_name, size=48, cls="mx-auto mb-4 opacity-40")
        )

    children.append(
        P(
            message,
            cls="text-base-content/60 text-center py-12",
        )
    )

    return Div(*children)