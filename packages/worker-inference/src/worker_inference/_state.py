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

# packages/worker-inference/src/worker_inference/_state.py
from transformers import Qwen3_5ForCausalLM, AutoTokenizer


model: Qwen3_5ForCausalLM | None = None
"""
Process-local model instance shared across all tasks in this worker.

Holds the eagerly loaded Qwen3_5ForCausalLM after successful worker startup.
None until main() in main.py completes initialization. Each worker process
maintains its own isolated instance of this module; no model state is shared
across processes. All tasks in this process read from this reference via
get_model().
"""

tokenizer: AutoTokenizer | None = None
"""
Process-local tokenizer instance shared across all tasks in this worker.

Loaded from the same model_path as the model during worker startup and held
for the lifetime of the process. None until main() in main.py completes
initialization.
"""