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

# packages/worker-inference/src/worker_inference/main.py
from transformers import Qwen3_5ForCausalLM, AutoTokenizer
from celery_lib import celery_config, celery_app
from . import _state
from .config import worker_inference_config

celery_app.autodiscover_tasks(["worker_inference.tasks"])


def get_model() -> Qwen3_5ForCausalLM:
    """
    Return the pre-initialized model for the current process.

    Provides tasks with access to the eagerly loaded Qwen3_5ForCausalLM
    instance. Raises a descriptive error if called before the worker
    startup sequence has completed.

    Returns
    -------
    Qwen3_5ForCausalLM
        Loaded model ready for synchronous inference on the current process.

    Raises
    ------
    RuntimeError
        Raised if the model was not initialized during worker startup,
        indicating a misconfiguration or premature task dispatch.
    """
    if _state.model is None:
        raise RuntimeError(
            "Inference model not initialized. "
            "Ensure main() executed successfully before task dispatch."
        )
    return _state.model


def get_tokenizer() -> AutoTokenizer:
    """
    Return the pre-initialized tokenizer for the current process.

    Provides tasks with access to the eagerly loaded AutoTokenizer instance.
    Raises a descriptive error if called before the worker startup sequence
    has completed.

    Returns
    -------
    AutoTokenizer
        Loaded tokenizer ready for encoding and decoding on the current process.

    Raises
    ------
    RuntimeError
        Raised if the tokenizer was not initialized during worker startup,
        indicating a misconfiguration or premature task dispatch.
    """
    if _state.tokenizer is None:
        raise RuntimeError(
            "Tokenizer not initialized. "
            "Ensure main() executed successfully before task dispatch."
        )
    return _state.tokenizer


def main() -> None:
    """
    Eagerly load the model and tokenizer, then launch the Celery worker.

    Both the model and tokenizer are loaded before entering the Celery worker
    loop to ensure fail-fast behavior on configuration errors and to eliminate
    cold-start latency for the first inference request. The worker consumes
    exclusively from the inference queue with solo pool and prefetch multiplier
    of 1 to ensure model weights occupy device memory without contention.

    Configuration is resolved from WORKER_INFERENCE_ prefixed environment
    variables via WorkerInferenceConfig.

    Returns
    -------
    None
        Blocks indefinitely while the Celery worker processes tasks from the
        inference queue. Terminates only on external SIGTERM or SIGKILL.
    """
    _state.tokenizer = AutoTokenizer.from_pretrained(
        worker_inference_config.model_path,
    )
    _state.model = Qwen3_5ForCausalLM.from_pretrained(
        worker_inference_config.model_path,
        device_map=worker_inference_config.device,
    )

    worker_argv = [
        "worker",
        "--hostname", worker_inference_config.name,
        "--queues", celery_config.queue_name_inference,
        "--pool", worker_inference_config._pool,
        "--prefetch-multiplier", str(worker_inference_config._prefetch_multiplier),
        "--loglevel", worker_inference_config.log_level,
    ]
    celery_app.worker_main(argv=worker_argv)


if __name__ == "__main__":
    main()