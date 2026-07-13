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

# packages/worker-maintenance/src/worker_maintenance/config.py
from typing import ClassVar, Final
from pathlib import Path
from base_lib import BaseConfig, LogLevel
from pydantic import model_validator


class WorkerMaintenanceConfig(BaseConfig):
    """
    Configuration schema for the maintenance Celery worker.

    Controls worker identity, logging, and execution environment for the
    maintenance worker process. All env-dependent fields support resolution
    from environment variables prefixed with WORKER_MAINTENANCE_ following
    the BaseConfig precedence rules.

    Attributes
    ----------
    name : str
        Celery worker name template. The %n placeholder is expanded by
        Celery to the short hostname at startup. Default is
        "worker_maintenance@%n".
    log_level : LogLevel
        Logging verbosity for the worker process. Default is "INFO".
    beat_schedule_path : str
        Filesystem path to the persistent beat schedule database file.
        The containing directory is created automatically on startup if
        it does not exist. Default is "celery-beat/celerybeat-schedule".
    beat_pidfile_path : str
        Filesystem path to the beat process pid file. Used to prevent
        more than one beat process from running simultaneously. If the
        pidfile already exists beat will refuse to start. The containing
        directory is created automatically on startup if it does not
        exist. Default is "/tmp/celerybeat.pid".
    _pool : str
        Celery worker pool implementation. Fixed to solo, which runs
        tasks sequentially in the main process without spawning child
        processes or threads. Appropriate for the maintenance worker
        since all tasks are lightweight database operations with no
        concurrency requirements.
    _prefetch_multiplier : int
        Number of tasks the worker fetches from the broker ahead of
        execution. Fixed to 1 so that at most one task sits in the
        local queue at a time.
    """

    env_prefix: ClassVar[str] = "WORKER_MAINTENANCE_"

    # ===== ENV-DEPENDENT (configurable via WORKER_MAINTENANCE_ prefixed env vars) =====
    name: str = "worker_maintenance@%n"
    log_level: LogLevel = "INFO"
    beat_schedule_path: str = "celery-beat/celerybeat-schedule"
    beat_pidfile_path: str = "celery-beat/celerybeat.pid"

    # ====== ARCHITECTURAL CONSTANTS (private, not configurable via env) ======
    _pool: Final[str] = "solo"
    _prefetch_multiplier: Final[int] = 1

    @model_validator(mode="after")
    def ensure_directories_exist(self) -> "WorkerMaintenanceConfig":
        """
        Create parent directories for beat_schedule_path and
        beat_pidfile_path if they do not already exist.

        Runs automatically after model instantiation so the filesystem
        is ready before any beat or worker process starts.

        Returns
        -------
        WorkerMaintenanceConfig
            The validated config instance unchanged.
        """
        Path(self.beat_schedule_path).parent.mkdir(parents=True, exist_ok=True)
        Path(self.beat_pidfile_path).parent.mkdir(parents=True, exist_ok=True)
        
        return self


worker_maintenance_config = WorkerMaintenanceConfig()