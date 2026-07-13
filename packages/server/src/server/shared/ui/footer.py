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

# packages/server/src/server/shared/ui/footer.py
from fasthtml.common import Footer, Div, A, Span, FT
from ...config import server_config


def _create_copyright_span() -> Span:
    """
    Create the copyright notice for the footer.

    Returns
    -------
    Span
        FastHTML span element displaying the copyright year and
        application name.
    """
    return Span(
        f"© 2026 {server_config.app_name}",
        cls="text-sm text-base-content/60",
    )


def _create_footer_link(
    label: str,
    href: str,
    *,
    external: bool = False,
) -> A:
    """
    Create a styled footer link.

    Parameters
    ----------
    label : str
        Visible link text.
    href : str
        Destination URL.
    external : bool
        Whether the link points to an external resource. When True,
        adds target and rel attributes to open safely in a new tab.
        Default is False.

    Returns
    -------
    A
        Styled FastHTML anchor element with optional icon.
    """
    attributes = {}

    if external:
        attributes.update(
            {
                "target": "_blank",
                "rel": "noopener noreferrer",
            }
        )

    children = []
    children.append(label)

    return A(
        *children,
        href=href,
        cls="link link-hover text-sm text-base-content/60 gap-1",
        **attributes,
    )


def create_footer() -> FT:
    """
    Create the global application footer.

    Displays application copyright information and navigation links.
    External destinations are opened safely in a new browser tab.

    Returns
    -------
    FT
        Footer element ready for page layout composition.
    """
    return Footer(
        Div(
            Div(
                _create_copyright_span(),
                cls="flex items-center",
            ),
            Div(
                _create_footer_link(
                    "GitHub",
                    server_config.github_url,
                    external=True,
                ),
                _create_footer_link(
                    "Privacy Policy",
                    server_config.privacy_policy_url,
                    external=True,
                ),
                cls="flex items-center gap-4",
            ),
            cls=(
                "container mx-auto px-4 py-6 "
                "flex items-center justify-between"
            ),
        ),
        cls="footer bg-base-100 border-t border-base-200 mt-auto",
    )