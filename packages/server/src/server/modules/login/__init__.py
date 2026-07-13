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

# packages/server/src/server/modules/login/__init__.py
from starlette.routing import Route
from .routes import login_get, login_post
from ...config import RoutePath

login_routes = [
    Route(RoutePath.LOGIN, endpoint=login_get, methods=["GET"]),
    Route(RoutePath.LOGIN, endpoint=login_post, methods=["POST"]),
]