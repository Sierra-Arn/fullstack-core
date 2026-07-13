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

# packages/scripts/src/scripts/quick_start.py
"""
Local development environment quick-start script.

Automates the full bootstrap process for running the application locally.
Sequentially generates configuration files, builds frontend assets, spins
up Docker infrastructure, applies database migrations, and launches all
worker processes and the web server in separate terminal windows. Upon
successful startup polls the health endpoint and automatically opens the
application in the default browser.

Execution sequence:

+------+-----------------------------+--------------------------------------------------------------+
| Step | Command                     | Description                                                  |
+======+=============================+==============================================================+
| 1    | ``just gen-env``            | Copies ``.env.example`` to ``.env`` in the project root and  |
|      |                             | generates cryptographically secure passwords for all         |
|      |                             | credential fields. Skipped if ``.env`` already exists.       |
+------+-----------------------------+--------------------------------------------------------------+
| 2    | ``just gen-acl``            | Generates ``redis/init/01-create-users.acl`` from            |
|      |                             | environment variables. Defines Redis users with scoped       |
|      |                             | permissions for the application.                             |
+------+-----------------------------+--------------------------------------------------------------+
| 3    | ``just gen-sql``            | Generates ``postgres/init/01-create-user.sql`` from          |
|      |                             | environment variables. Creates the application database      |
|      |                             | user with the minimum required privileges.                   |
+------+-----------------------------+--------------------------------------------------------------+
| 4    | ``just build-css``          | Compiles Tailwind CSS and DaisyUI from the source input      |
|      |                             | file into the static output file consumed by the server.     |
+------+-----------------------------+--------------------------------------------------------------+
| 5    | ``just build-js``           | Bundles HTMX and Alpine.js from the source entry file        |
|      |                             | into the static output file consumed by the server.          |
+------+-----------------------------+--------------------------------------------------------------+
| 6    | ``just build-icons``        | Copies Heroicons SVG files from node_modules into the        |
|      |                             | static icons directory consumed by the server.               |
+------+-----------------------------+--------------------------------------------------------------+
| 7    | ``just docker-up``          | Starts the Docker Compose stack: PostgreSQL and Redis.       |
+------+-----------------------------+--------------------------------------------------------------+
| 8    | *(10s pause)*               | Waits for infrastructure containers to become healthy        |
|      |                             | before proceeding.                                           |
+------+-----------------------------+--------------------------------------------------------------+
| 9    | ``just db-migrate``         | Applies all pending Alembic migrations to bring the          |
|      |                             | database schema to the current version.                      |
+------+-----------------------------+--------------------------------------------------------------+
| 10   | ``just worker-inference``   | Launches the Celery inference worker in a new terminal       |
|      |                             | window. Eagerly loads the Qwen3.5-2B model into              |
|      |                             | memory before entering the task loop.                        |
+------+-----------------------------+--------------------------------------------------------------+
| 11   | ``just worker-maintenance`` | Launches the Celery maintenance worker in a new terminal     |
|      |                             | window. Consumes tasks from the maintenance queue,           |
|      |                             | including the daily inference run counter reset.             |
+------+-----------------------------+--------------------------------------------------------------+
| 12   | ``just worker-beat``        | Launches the Celery beat scheduler in a new terminal         |
|      |                             | window. Dispatches scheduled maintenance tasks into the      |
|      |                             | maintenance queue according to the configured schedule.      |
+------+-----------------------------+--------------------------------------------------------------+
| 13   | ``just server``             | Launches the FastHTML/Uvicorn web server in a new terminal   |
|      |                             | window.                                                      |
+------+-----------------------------+--------------------------------------------------------------+
| 14   | *(health polling)*          | Polls ``GET /health/shallow/`` until the server responds     |
|      |                             | with HTTP 200 or the retry limit is reached.                 |
+------+-----------------------------+--------------------------------------------------------------+
| 15   | *(browser opening)*         | On successful health check, automatically opens the          |
|      |                             | application landing page in the default browser. If the      |
|      |                             | server fails to respond in time, prints a warning with       |
|      |                             | the manual URL.                                              |
+------+-----------------------------+--------------------------------------------------------------+

Usage
-----
pixi run python -m scripts.quick_start

Note
----
The exact shell commands executed by each just recipe are defined in the
project's justfile at the repository root. Refer to the justfile for the
authoritative step-by-step implementation details of the bootstrap sequence.
"""
import os
import sys
import time
import subprocess
import webbrowser
from pathlib import Path
from urllib.request import urlopen
from urllib.error import URLError
from dotenv import load_dotenv


def _run(cmd: list[str]) -> None:
    """
    Execute a subprocess command and block until it completes.

    Parameters
    ----------
    cmd : list[str]
        Command and arguments passed directly to subprocess.
    """
    print(f"\n>>> {' '.join(cmd)}")
    result = subprocess.run(cmd)
    if result.returncode != 0:
        sys.exit(result.returncode)


def _terminal(cmd: list[str]) -> None:
    """
    Open a new gnome-terminal window and execute a command inside it.

    Parameters
    ----------
    cmd : list[str]
        Command and arguments to run inside the new terminal window.
    """
    print(f"\n>>> gnome-terminal: {' '.join(cmd)}")
    subprocess.Popen(["gnome-terminal", "--", "bash", "-c", " ".join(cmd)])


def _get_server_url() -> tuple[str, str]:
    """
    Load environment variables and construct the server base URL and health URL.

    Returns
    -------
    tuple[str, str]
        A pair of (health_url, base_url) constructed from SERVER_HOST
        and SERVER_PORT environment variables.
    """
    load_dotenv(Path.cwd() / ".env")

    host = os.getenv("SERVER_HOST")
    port = os.getenv("SERVER_PORT")

    base_url = f"http://{host}:{port}"
    return f"{base_url}/health/shallow/", base_url


def _start_infrastructure() -> None:
    """
    Generate environment configurations, build frontend assets, start
    Docker containers, and apply database migrations.
    """
    print("[info] initializing environment and infrastructure...")

    _run(["just", "gen-env"])
    _run(["just", "gen-acl"])
    _run(["just", "gen-sql"])
    _run(["just", "build-css"])
    _run(["just", "build-js"])
    _run(["just", "build-icons"])
    _run(["just", "docker-up"])

    print("[info] waiting for infrastructure to start...")
    time.sleep(10)

    _run(["just", "db-migrate"])


def _wait_for_server(
    health_url: str,
    retries: int = 20,
    interval: int = 10,
) -> bool:
    """
    Poll the health endpoint until it returns HTTP 200 or the retry limit is reached.

    Parameters
    ----------
    health_url : str
        URL of the shallow health endpoint to poll.
    retries : int
        Maximum number of attempts before giving up. Default is 20.
    interval : int
        Number of seconds to wait between attempts. Default is 10.

    Returns
    -------
    bool
        True if the server responded with HTTP 200 within the retry limit.
        False if all attempts were exhausted without a successful response.
    """
    print(f"\n[info] waiting for server at {health_url}")
    for _ in range(retries):
        try:
            with urlopen(health_url, timeout=2) as response:
                if response.status == 200:
                    return True
        except (URLError, OSError):
            pass
        time.sleep(interval)
    return False


if __name__ == "__main__":
    _start_infrastructure()

    _terminal(["just", "worker-inference"])
    _terminal(["just", "worker-maintenance"])
    _terminal(["just", "worker-beat"])
    _terminal(["just", "server"])

    health_url, base_url = _get_server_url()

    if _wait_for_server(health_url):
        print(f"\n[info] server is healthy, opening {base_url}")
        webbrowser.open(base_url)
    else:
        print(f"[warn] server did not respond in time, open manually: {base_url}")