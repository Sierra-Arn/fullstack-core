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

# packages/worker-inference/src/worker_inference/config.py
from typing import ClassVar, Final, Literal
from base_lib import BaseConfig, LogLevel


class WorkerInferenceConfig(BaseConfig):
    """
    Configuration schema for the inference Celery worker.

    Controls worker identity, model loading, and execution environment.
    All env-dependent fields support resolution from environment variables
    prefixed with WORKER_INFERENCE_ following the BaseConfig precedence rules.

    Attributes
    ----------
    name : str
        Celery worker name template. The %n placeholder is expanded by
        Celery to the short hostname at startup. Default is
        "worker_inference@%n".
    model_path : str
        HuggingFace model identifier or local filesystem path passed
        to from_pretrained at worker startup. The model is loaded once
        and held in memory for the lifetime of the worker process.
        Default is "Qwen/Qwen3.5-2B".
    device : Literal["cpu", "cuda"]
        Torch device on which the model is loaded and inference is executed.
        Default is "cuda".
    log_level : LogLevel
        Logging verbosity for the worker process. Default is "INFO".
    _pool : str
        Celery worker pool implementation. Fixed to solo, which runs
        tasks sequentially in the main process without spawning child
        processes or threads, ensuring the loaded model is never shared
        across concurrent execution contexts.
    _prefetch_multiplier : str
        Number of tasks the worker fetches from the broker ahead of
        execution. Fixed to 1 so that at most one task sits in the
        local queue at a time, preventing a backlog from accumulating
        in the worker process while the model is busy.
    """

    env_prefix: ClassVar[str] = "WORKER_INFERENCE_"

    # ===== ENV-DEPENDENT (configurable via WORKER_INFERENCE_ prefixed env vars) =====
    name: str = "worker_inference@%n"
    model_path: str = "Qwen/Qwen3.5-2B"
    device: Literal["cpu", "cuda"] = "cuda"
    log_level: LogLevel = "INFO"

    # ====== ARCHITECTURAL CONSTANTS (private, not configurable via env) ======
    _pool: Final[str] = "solo"
    _prefetch_multiplier: Final[int] = 1


worker_inference_config = WorkerInferenceConfig()