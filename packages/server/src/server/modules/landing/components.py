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

# packages/server/src/server/modules/landing/components.py
from fasthtml.common import Div, H3, P, FT
from ...shared import create_icon


def create_feature_card(
    title: str,
    description: str,
    icon_name: str,
) -> FT:
    """
    Create a capability card for the landing page features section.

    All content (icon, title, description) is centered both horizontally
    and vertically within the card body using flexbox alignment.

    Parameters
    ----------
    title : str
        Heading text displayed at the top of the card.
    description : str
        Explanatory text detailing the specific capability.
    icon_name : str
        Heroicon name displayed prominently at the top of the card.

    Returns
    -------
    FT
        FastHTML card element styled for the capabilities grid.
    """
    return Div(
        Div(
            create_icon(icon_name, size=32, cls="text-primary"),
            H3(
                title,
                cls="card-title text-xl",
            ),
            P(
                description,
                cls="text-base-content/60",
            ),
            cls="card-body items-center text-center",
        ),
        cls="card bg-base-100 shadow-sm",
    )


def create_step_card(
    number: int,
    title: str,
    description: str,
) -> FT:
    """
    Create a step card for the how-it-works section.

    All content (number, title, description) is centered both
    horizontally and vertically within the card using flexbox alignment.

    Parameters
    ----------
    number : int
        Sequential step number displayed prominently at the top.
    title : str
        Heading text describing the step action.
    description : str
        Explanatory text providing details about the step.

    Returns
    -------
    FT
        FastHTML card element styled for the step-by-step grid.
    """
    return Div(
        Div(
            str(number),
            cls="text-4xl font-bold text-primary",
        ),
        H3(
            title,
            cls="text-xl font-semibold mt-4",
        ),
        P(
            description,
            cls="text-base-content/60 mt-2",
        ),
        cls="card bg-base-100 shadow-sm p-6 flex flex-col items-center text-center",
    )