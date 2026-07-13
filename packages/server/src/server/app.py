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

# Originally from Backend Core
# https://github.com/Sierra-Arn/backend-core
# Modified for Full-Stack Core

# packages/server/src/server/app.py
from pathlib import Path
from fasthtml.common import FastHTML
from starlette.exceptions import HTTPException
from starlette.staticfiles import StaticFiles
from .config import server_config
from .exception_handlers import (
    http_exception_handler,
    unhandled_exception_handler,
)
from .middleware import AccessLogMiddleware, RateLimitMiddleware
from .modules import all_routes


def create_app() -> FastHTML:
    """
    Factory function for initializing the FastHTML application instance.

    Assembles all route lists into a single routing table, registers
    middleware in reverse execution order, attaches exception handlers,
    and mounts the static files directory. Returns a fully configured
    ASGI application ready for deployment.

    Returns
    -------
    FastHTML
        Configured application instance with routes, middleware,
        exception handlers, and static files bound.
    """
    app = FastHTML(
        routes=all_routes,
        sess_cls=server_config._session_class,
        surreal=server_config._surreal_enabled,
        htmx=server_config._htmx_enabled,
        default_hdrs=server_config._default_headers_enabled,
    )

    # Order matters: handlers must be registered from most specific to most general.
    # FastHTML matches the first handler whose exception type matches or is a parent
    # of the raised exception. Registering Exception first would cause it to
    # intercept HTTPException before its dedicated handler has a chance to run.
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)

    # Middleware is applied in reverse registration order. The last registered
    # middleware wraps the outermost layer of the request. AccessLogMiddleware
    # is registered first so that it runs last, ensuring it captures the final
    # response status code after all other middleware has processed the request.
    # RateLimitMiddleware is registered second so that it runs first, enforcing
    # rate limits before any other middleware or route handler executes.
    app.add_middleware(AccessLogMiddleware)
    app.add_middleware(RateLimitMiddleware)

    # Static files are mounted at the /static URL prefix to serve all frontend
    # assets including CSS stylesheets, JavaScript bundles, and Heroicons SVG files.
    # The directory path points to the compiled output location where build-css,
    # build-js, and build-icons recipes place their artifacts. Using Path.cwd()
    # ensures the path resolves correctly regardless of the working directory from
    # which the application is launched. The name parameter provides a unique
    # identifier for the mount point, enabling reverse URL generation through
    # Starlette's url_for mechanism if needed in the future.
    app.mount(
        "/static",
        StaticFiles(
            directory=Path.cwd() / "packages" / "server" / "static",
        ),
        name="static",
    )

    return app