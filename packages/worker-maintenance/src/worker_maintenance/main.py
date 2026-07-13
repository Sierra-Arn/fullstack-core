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

# packages/worker-maintenance/src/worker_maintenance/main.py
import argparse
from celery_lib import celery_config, celery_app
from .config import worker_maintenance_config


def _parse_args() -> argparse.Namespace:
    """
    Parse command-line arguments for the maintenance worker.

    Returns
    -------
    argparse.Namespace
        Parsed arguments containing the mode to run: either worker
        or beat.
    """
    parser = argparse.ArgumentParser(
        description="Maintenance worker. Run either the Celery worker or the beat scheduler.",
    )
    parser.add_argument(
        "--mode",
        type=str,
        choices=["worker", "beat"],
        required=True,
        help="worker: consume tasks from the maintenance queue. beat: dispatch scheduled tasks.",
    )
    return parser.parse_args()


def run_worker() -> None:
    """
    Launch the Celery worker consuming from the maintenance queue.

    Loads all maintenance tasks via autodiscover and starts the worker
    in solo pool mode with a prefetch multiplier of 1. Blocks indefinitely
    until terminated by SIGTERM or SIGKILL.

    Returns
    -------
    None
    """
    celery_app.autodiscover_tasks(["worker_maintenance.tasks"])

    worker_argv = [
        "worker",
        "--hostname", worker_maintenance_config.name,
        "--queues", celery_config.queue_name_maintenance,
        "--pool", worker_maintenance_config._pool,
        "--prefetch-multiplier", str(worker_maintenance_config._prefetch_multiplier),
        "--loglevel", worker_maintenance_config.log_level,
    ]
    celery_app.worker_main(argv=worker_argv)


def run_beat() -> None:
    """
    Launch the Celery beat scheduler.

    Dispatches scheduled tasks into the maintenance queue according to
    the beat_schedule configured in celery_lib. The --pidfile flag
    prevents more than one beat process from running simultaneously. If a
    pidfile already exists beat will refuse to start, avoiding
    duplicate task dispatch. Both paths are resolved from
    worker_maintenance_config so they can be overridden via environment
    variables without code changes.

    Returns
    -------
    None
        Blocks indefinitely while the beat scheduler runs. Terminates
        only on external SIGTERM or SIGKILL.
    """
    beat_argv = [
        "beat",
        "--loglevel", worker_maintenance_config.log_level,
        "--pidfile", worker_maintenance_config.beat_pidfile_path,
        "--schedule", worker_maintenance_config.beat_schedule_path,
    ]
    celery_app.start(argv=beat_argv)


def main() -> None:
    """
    Entry point for the maintenance worker package.

    Parses the --mode argument and delegates to either run_worker or
    run_beat. Both modes block indefinitely until the process is
    terminated externally.

    Returns
    -------
    None
    """
    args = _parse_args()

    if args.mode == "worker":
        run_worker()
    else:
        run_beat()


if __name__ == "__main__":
    main()