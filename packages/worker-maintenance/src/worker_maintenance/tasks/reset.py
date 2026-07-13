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

# packages/worker-maintenance/src/worker_maintenance/tasks/reset.py
from celery_lib import celery_config, celery_app
from postgres_lib import get_sync_db_session
from postgres_lib.models import User
from sqlalchemy import update


@celery_app.task(
    name=celery_config.task_name_reset_inference_counts,
    queue=celery_config.queue_name_maintenance,
)
def reset_inference_counts_task() -> dict[str, int]:
    """
    Reset the inference run counter for all user accounts.

    Dispatched daily by Celery beat at the UTC hour configured via
    celery_config.hour_reset_inference_counts and consumed exclusively
    from the maintenance queue. Issues a single bulk UPDATE statement
    rather than fetching and updating records individually, so execution
    time is independent of the number of registered users.

    The result is stored in the Celery result backend for the duration
    of result_expires so that the outcome of each daily reset can be
    inspected after the fact for operational verification.

    Returns
    -------
    dict[str, int]
        Dictionary containing rows_updated with the number of user
        records affected by the reset. Equals the total number of
        registered users at the time of execution since the UPDATE
        targets all rows unconditionally.
    """
    with get_sync_db_session() as session:
        result = session.execute(
            update(User).values(inference_runs_count=0)
        )
        session.commit()

    return {"rows_updated": result.rowcount}