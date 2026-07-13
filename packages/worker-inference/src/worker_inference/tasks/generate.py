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

# packages/worker-inference/src/worker_inference/tasks/generate.py
from transformers import PreTrainedTokenizerBase
from sqlalchemy import update
from celery_lib import celery_config, celery_app
from postgres_lib import get_sync_db_session
from postgres_lib.models import InferenceHistory, User
from ..main import get_model, get_tokenizer


@celery_app.task(
    name=celery_config.task_name_inference,
    queue=celery_config.queue_name_inference,
)
def generate_task(
    input_text: str,
    user_id: int,
    max_new_tokens: int = 512,
) -> dict[str, str]:
    """
    Run text generation on the pre-loaded Qwen model, persist the result
    to the database, and increment the user's inference run counter.

    Parameters
    ----------
    input_text : str
        Raw text submitted by the user as the model prompt.
    user_id : int
        Primary key of the authenticated user who submitted the request.
        Used to associate the inference record and increment the run counter.
    max_new_tokens : int, optional
        Maximum number of tokens the model may generate in response.
        Default is 512.

    Returns
    -------
    dict[str, str]
        Dictionary containing input_text and output_text, both stored
        in the Celery result backend so the web process can render the
        result partial without an additional database query.

    Raises
    ------
    RuntimeError
        If the model or tokenizer were not initialized during worker
        startup, or if the model returns an empty output sequence.
    """
    model = get_model()
    tokenizer: PreTrainedTokenizerBase = get_tokenizer()

    messages = [{"role": "user", "content": input_text}]
    inputs = tokenizer.apply_chat_template(
        messages,
        add_generation_prompt=True,
        return_tensors="pt",
        return_dict=True,
    ).to(model.device)

    generated_ids = model.generate(
        **inputs,
        max_new_tokens=max_new_tokens,
        pad_token_id=tokenizer.eos_token_id,
    )

    output_ids = generated_ids[0][inputs["input_ids"].shape[-1]:]
    output_text = tokenizer.decode(output_ids, skip_special_tokens=True)

    if not output_text:
        raise RuntimeError(
            "Model returned an empty output sequence. "
            "The prompt may be malformed or max_new_tokens too low."
        )

    with get_sync_db_session() as session:
        session.add(InferenceHistory(
            user_id=user_id,
            input_text=input_text,
            output_text=output_text,
        ))
        session.execute(
            update(User)
            .where(User.id == user_id)
            .values(inference_runs_count=User.inference_runs_count + 1)
        )
        session.commit()

    return {
        "input_text": input_text,
        "output_text": output_text,
    }