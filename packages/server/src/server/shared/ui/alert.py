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

# packages/server/src/server/shared/ui/alert.py
from enum import StrEnum
from fasthtml.common import Div, Span, FT
from ..utils import create_icon


class Alert(StrEnum):
    """
    Visual severity variants for feedback alerts.

    Attributes
    ----------
    INFO : Alert
        Informational message.
    SUCCESS : Alert
        Successful operation confirmation.
    WARNING : Alert
        Potential issue or cautionary notice.
    ERROR : Alert
        Failure or critical error notification.
    """

    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"


_ALERT_CLASSES: dict[Alert, str] = {
    Alert.INFO: "alert alert-info",
    Alert.SUCCESS: "alert alert-success",
    Alert.WARNING: "alert alert-warning",
    Alert.ERROR: "alert alert-error",
}


_ALERT_ICONS: dict[Alert, str] = {
    Alert.INFO: "information-circle",
    Alert.SUCCESS: "check-circle",
    Alert.WARNING: "exclamation-triangle",
    Alert.ERROR: "x-circle",
}


def _create_alert_icon(alert_type: Alert) -> FT:
    """
    Create the decorative icon for an alert.

    The icon is hidden from assistive technologies because the message
    text conveys the actual information.

    Parameters
    ----------
    alert_type : Alert
        The severity variant determining which icon to display.

    Returns
    -------
    FT
        FastHTML img element containing the Heroicon.
    """
    return create_icon(
        _ALERT_ICONS[alert_type],
        size=24,
        cls="shrink-0",
    )


def create_alert(
    message: str,
    alert_type: Alert = Alert.INFO,
    *,
    show_icon: bool = True,
) -> FT:
    """
    Create an inline feedback alert component.

    Designed for server-rendered feedback messages and HTMX partial
    replacements. This component strictly handles presentation logic
    and does not contain any business logic or state management.

    Parameters
    ----------
    message : str
        Human-readable text displayed to the user inside the alert.
    alert_type : Alert
        Visual severity variant that determines the color scheme and
        icon of the alert. Default is INFO.
    show_icon : bool
        Whether to display the leading decorative Heroicon.
        Default is True.

    Returns
    -------
    FT
        Fully assembled FastHTML alert element ready for rendering.
    """
    children: list[FT] = []

    if show_icon:
        children.append(_create_alert_icon(alert_type))

    children.append(Span(message))

    return Div(
        *children,
        cls=_ALERT_CLASSES[alert_type],
        role="alert",
    )


def create_form_alert_slot(
    *,
    error: str | None = None,
    success: str | None = None,
) -> FT:
    """
    Create the feedback slot rendered above an HTMX form.

    Provides a stable, uniquely identified container into which route
    handlers render their alerts. Keeping the slot as a dedicated sibling
    above the input fields guarantees that error and success messages appear
    over the form rather than replacing it, and that repeated messages
    replace the previous one instead of accumulating.

    The slot is always rendered, even when empty, so its position in the
    layout stays stable across submissions.

    Parameters
    ----------
    error : str or None
        Optional error message. When provided, an error alert is rendered
        inside the slot. Default is None.
    success : str or None
        Optional success message. When provided, a success alert is
        rendered inside the slot. Default is None.

    Returns
    -------
    FT
        FastHTML div container carrying the conventional form alert id,
        holding the conditional success and error alerts.
    """
    children: list[FT] = []

    if success:
        children.append(create_alert(success, Alert.SUCCESS))

    if error:
        children.append(create_alert(error, Alert.ERROR))

    return Div(
        *children,
        id="form-alert",
    )