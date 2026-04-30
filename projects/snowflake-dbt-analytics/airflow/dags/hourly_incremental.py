"""
hourly_incremental.py
---------------------
Airflow DAG: Incremental load for high-frequency sources (events + tickets).
Runs every hour. Only processes new/updated records since last run.

Schedule: 0 * * * *
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.providers.slack.operators.slack_webhook import SlackWebhookOperator
from airflow.models import Variable

DBT_PROJECT_DIR = Variable.get("dbt_project_dir", default_var="/opt/dbt/snowflake_analytics")
DBT_PROFILES_DIR = Variable.get("dbt_profiles_dir", default_var="/opt/dbt/profiles")
SLACK_WEBHOOK_CONN = "slack_webhook_analytics"

default_args = {
    "owner": "analytics-eng",
    "depends_on_past": False,
    "email_on_failure": True,
    "email": ["analytics@company.com"],
    "retries": 3,
    "retry_delay": timedelta(minutes=2),
    "retry_exponential_backoff": True,
}


def on_failure_callback(context):
    dag_id = context["dag"].dag_id
    task_id = context["task_instance"].task_id
    log_url = context["task_instance"].log_url

    slack_alert = SlackWebhookOperator(
        task_id="slack_failure_alert",
        http_conn_id=SLACK_WEBHOOK_CONN,
        message=(
            f":warning: *Incremental Load Failed*\n"
            f"*DAG:* `{dag_id}` | *Task:* `{task_id}`\n"
            f"*Log:* <{log_url}|View Logs>"
        ),
        dag=context["dag"],
    )
    return slack_alert.execute(context=context)


with DAG(
    dag_id="hourly_incremental",
    description="Incremental dbt refresh for Amplitude events and Zendesk tickets",
    schedule_interval="0 * * * *",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    default_args=default_args,
    on_failure_callback=on_failure_callback,
    tags=["dbt", "analytics", "incremental", "hourly"],
    max_active_runs=1,  # Prevent overlapping runs
) as dag:

    # Incremental run for Amplitude events staging model
    dbt_run_amplitude = BashOperator(
        task_id="dbt_run_amplitude_events",
        bash_command=(
            f"cd {DBT_PROJECT_DIR} && "
            f"dbt run --select stg_amplitude__events "
            f"--profiles-dir {DBT_PROFILES_DIR} --target prod"
        ),
    )

    # Incremental run for Zendesk tickets staging model
    dbt_run_zendesk = BashOperator(
        task_id="dbt_run_zendesk_tickets",
        bash_command=(
            f"cd {DBT_PROJECT_DIR} && "
            f"dbt run --select stg_zendesk__tickets "
            f"--profiles-dir {DBT_PROFILES_DIR} --target prod"
        ),
    )

    # Rebuild support load fact (depends on fresh ticket data)
    dbt_run_support_load = BashOperator(
        task_id="dbt_run_fct_support_load",
        bash_command=(
            f"cd {DBT_PROJECT_DIR} && "
            f"dbt run --select fct_support_load "
            f"--profiles-dir {DBT_PROFILES_DIR} --target prod"
        ),
    )

    # Run tests on incremental models only
    dbt_test_incremental = BashOperator(
        task_id="dbt_test_incremental",
        bash_command=(
            f"cd {DBT_PROJECT_DIR} && "
            f"dbt test --select stg_amplitude__events stg_zendesk__tickets fct_support_load "
            f"--profiles-dir {DBT_PROFILES_DIR} --target prod"
        ),
    )

    # Parallel ingestion, then sequential downstream
    [dbt_run_amplitude, dbt_run_zendesk] >> dbt_run_support_load >> dbt_test_incremental