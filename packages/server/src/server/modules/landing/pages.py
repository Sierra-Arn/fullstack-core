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

# packages/server/src/server/modules/landing/pages.py
from fasthtml.common import Div, H1, H2, P, A, Section, FT
from postgres_lib import Role
from .components import create_feature_card, create_step_card
from ...config import RoutePath
from ...shared.ui import create_layout


def _create_hero_cta(role: Role) -> FT:
    """
    Create the call-to-action buttons for the hero section.

    Dynamically adapts based on the user authorization role, presenting
    registration options for unauthenticated visitors and direct navigation
    for authenticated users.

    Parameters
    ----------
    role : Role
        Resolved access role of the current user.

    Returns
    -------
    FT
        FastHTML container with call-to-action buttons.
    """
    if role.level < Role.USER.level:
        return Div(
            A(
                "Get Started",
                href=RoutePath.REGISTER,
                cls="btn btn-primary btn-lg",
            ),
            A(
                "Work with us",
                href=RoutePath.COLLABORATE,
                cls="btn btn-ghost btn-lg",
            ),
            cls="flex gap-4 justify-center",
        )

    return A(
        "Go to Inference",
        href=RoutePath.INFERENCE,
        cls="btn btn-primary btn-lg",
    )


def _create_hero_section(role: Role) -> Section:
    """
    Create the hero section for the landing page.

    Parameters
    ----------
    role : Role
        Resolved access role of the current user.

    Returns
    -------
    Section
        FastHTML section element containing the hero content.
    """
    return Section(
        Div(
            H1(
                "Test our Innovative LLM Model",
                cls="text-5xl font-bold",
            ),
            P(
                "Generate responses with an AI inference platform "
                "built with modern server-side rendering technologies.",
                cls=(
                    "text-xl text-base-content/70 "
                    "max-w-2xl mx-auto mt-6 mb-10"
                ),
            ),
            _create_hero_cta(role),
            cls="text-center",
        ),
        cls=(
            "hero min-h-[60vh] "
            "bg-gradient-to-br "
            "from-primary/20 via-base-200 to-secondary/20"
        ),
    )


def _create_capabilities_section() -> Section:
    """
    Create the capabilities overview section for the landing page.

    Returns
    -------
    Section
        FastHTML section element containing the feature cards grid.
    """
    return Section(
        Div(
            H2(
                "Capabilities",
                cls="text-3xl font-bold text-center mb-12",
            ),
            Div(
                create_feature_card(
                    "Advanced Text Generation",
                    "Generate context-aware responses "
                    "for complex language tasks.",
                    icon_name="document-text",
                ),
                create_feature_card(
                    "Fast Inference",
                    "Optimized processing pipeline "
                    "for responsive AI interactions.",
                    icon_name="bolt",
                ),
                create_feature_card(
                    "Secure & Private",
                    "Your prompts and results are "
                    "protected inside your account.",
                    icon_name="shield-check",
                ),
                cls="grid grid-cols-1 md:grid-cols-3 gap-6",
            ),
            cls="container mx-auto px-4",
        ),
        cls="py-20 bg-base-200",
    )


def _create_how_it_works_section() -> Section:
    """
    Create the step-by-step guide section for the landing page.

    Returns
    -------
    Section
        FastHTML section element containing the step cards grid.
    """
    return Section(
        Div(
            H2(
                "How it works",
                cls="text-3xl font-bold text-center mb-12",
            ),
            Div(
                create_step_card(
                    1,
                    "Create an account",
                    "Register and unlock your personal inference workspace.",
                ),
                create_step_card(
                    2,
                    "Submit your prompt",
                    "Send your request to the model with one click.",
                ),
                create_step_card(
                    3,
                    "Get your response",
                    "Receive generated output from the model.",
                ),
                cls="grid grid-cols-1 md:grid-cols-3 gap-6",
            ),
            cls="container mx-auto px-4",
        ),
        cls="py-20 bg-base-100",
    )


def create_landing_page(
    role: Role = Role.UNAUTHENTICATED,
) -> FT:
    """
    Create the public landing page of the application.

    Assembles the complete landing page layout, including the hero section,
    capabilities overview, and step-by-step guide. The call-to-action
    dynamically adapts based on the user authorization role, presenting
    registration options for unauthenticated visitors and direct navigation
    for authenticated users. Authentication state is resolved outside this
    module and passed in as a parameter.

    Parameters
    ----------
    role : Role
        Resolved access role of the current user. Determines which
        call-to-action buttons are displayed in the hero section.
        Default is UNAUTHENTICATED for anonymous visitors.

    Returns
    -------
    FT
        Fully assembled FastHTML document containing the complete
        landing page layout.
    """
    return create_layout(
        _create_hero_section(role),
        _create_capabilities_section(),
        _create_how_it_works_section(),
        title="Landing",
        role=role,
        contained=False,
    )