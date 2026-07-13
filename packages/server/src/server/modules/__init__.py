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

# packages/server/src/server/modules/__init__.py
from .health import health_routes
from .landing import landing_routes
from .register import register_routes
from .login import login_routes
from .logout import logout_routes
from .collaborate import collaborate_routes
from .inference import inference_routes
from .inference_history import inference_history_routes
from .leads import leads_routes
from .users import users_routes

all_routes = [
    *health_routes,
    *landing_routes,
    *register_routes,
    *login_routes,
    *logout_routes,
    *collaborate_routes,
    *inference_routes,
    *inference_history_routes,
    *leads_routes,
    *users_routes,
]