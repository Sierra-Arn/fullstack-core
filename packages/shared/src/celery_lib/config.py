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

# Originally from Human Pose Estimation Service
# https://github.com/Sierra-Arn/pose-estimation-service
# Modified for Full-Stack Core

# packages/shared/src/celery_lib/config.py
from typing import ClassVar, Final
from base_lib import BaseConfig


class CeleryConfig(BaseConfig):
    """
    Configuration schema for Celery task queue service connectivity.

    Stores connection parameters for accessing a Redis-backed Celery broker
    and result backend. All fields support resolution from environment
    variables prefixed with CELERY_ following the BaseConfig precedence
    rules.

    Attributes
    ----------
    app_name : str
        Human-readable identifier for the Celery application instance.
        Default is "fullstack-backend".
    result_expires : int
        Time-to-live in seconds for stored task results before automatic
        cleanup. Default is 3600.
    queue_name_inference : str
        Queue identifier for routing ML inference and text generation tasks
        to the inference worker. Default is "inference-queue".
    task_name_inference : str
        Registered task name for LLM text generation dispatched by the
        web server and consumed by the inference worker. Default is "generate".
    queue_name_maintenance : str
        Queue identifier for routing scheduled maintenance tasks dispatched
        by Celery beat and consumed by the maintenance worker. Kept separate
        from the inference queue so periodic tasks never compete with model
        inference for worker capacity. Default is "maintenance-queue".
    task_name_reset_inference_counts : str
        Registered task name for the daily inference run counter reset
        dispatched by Celery beat and consumed by the maintenance worker.
        Default is "reset_inference_counts".
    exchange_name : str
        Name of the shared exchange used for binding task queues and routing
        messages. Default is "tasks".
    schedule_name_reset_inference_counts : str
        Internal identifier for the daily inference run counter reset entry
        in the Celery beat schedule. Fixed and not configurable via environment.
        Default is "reset-inference-counts-daily".
    hour_reset_inference_counts : int
        UTC hour at which the daily inference run counter reset is scheduled.
        Accepts values in the range 0–23. Default is 0.
    minute_reset_inference_counts : int
        UTC minute within the configured hour at which the daily inference
        run counter reset is scheduled. Accepts values in the range 0–59.
        Default is 0. Combined with hour_reset_inference_counts, the default
        values schedule the reset at exactly midnight UTC.
    _schedule_name_reset : str
        Internal identifier for the reset task entry in the Celery beat
        schedule. Fixed and not configurable via environment.
    _task_serializer : str
        Serialization format for task arguments and kwargs passed to workers.
        Default is "json".
    _result_serializer : str
        Serialization format for task return values stored in the result
        backend. Default is "json".
    _accept_content : list of str
        Whitelist of content types the worker will deserialize.
        Default is ["json"].
    _timezone : str
        IANA timezone identifier used for scheduling and timestamp
        serialization. Default is "UTC".
    _enable_utc : bool
        Whether all internal timestamps use UTC. Default is True.
    _exchange_type : str
        Exchange routing strategy for Celery message delivery.
        Default is "direct".
    """

    env_prefix: ClassVar[str] = "CELERY_"

    # ======= ENV-DEPENDENT (configurable via CELERY_ prefixed env vars) =======

    app_name: str = "fullstack-backend"
    result_expires: int = 3600
    queue_name_inference: str = "inference-queue"
    task_name_inference: str = "generate"
    queue_name_maintenance: str = "maintenance-queue"
    task_name_reset_inference_counts: str = "reset_inference_counts"
    exchange_name: str = "tasks"
    schedule_name_reset_inference_counts: Final[str] = "reset-inference-counts-daily"
    hour_reset_inference_counts: int = 0
    minute_reset_inference_counts: int = 0

    # ======= ARCHITECTURAL CONSTANTS (private, not configurable via env) =======

    _task_serializer: Final[str] = "json"
    _result_serializer: Final[str] = "json"
    _accept_content: Final[list[str]] = ["json"]
    _timezone: Final[str] = "UTC"
    _enable_utc: Final[bool] = True
    _exchange_type: Final[str] = "direct"


celery_config = CeleryConfig()