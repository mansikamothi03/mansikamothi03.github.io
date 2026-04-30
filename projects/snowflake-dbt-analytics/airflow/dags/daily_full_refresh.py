"""
daily_full_refresh.py
---------------------
Airflow DAG: Full refresh of all dbt staging and mart models.
Runs daily at 02:00 UTC. Sends Slack alert on failure.

Schedule: 0 2 * * *
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
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
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}


def on_failure_callback(context):
    """Send Slack alert on DAG failure."""
    dag_id = context["dag"].dag_id
    task_id = context["task_instance"].task_id
    execution_date = context["execution_date"]
    log_url = context["task_instance"].log_url

    message = (
        f":red_circle: *DAG Failed*\n"
        f"*DAG:* `{dag_id}`\n"
        f"*Task:* `{task_id}`\n"
        f"*Execution Date:* {execution_date}\n"
        f"*Log:* <{log_url}|View Logs>"
    )

    slack_alert = SlackWebhookOperator(
        task_id="slack_failure_alert",
        http_conn_id=SLACK_WEBHOOK_CONN,
        message=message,
        dag=context["dag"],
    )
    return slack_alert.execute(context=context)


with DAG(
    dag_id="daily_full_refresh",
    description="Full dbt refresh: staging → intermediate → marts → metrics",
    schedule_interval="0 2 * * *",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    default_args=default_args,
    on_failure_callback=on_failure_callback,
    tags=["dbt", "analytics", "daily"],
) as dag:

    dbt_debug = BashOperator(
        task_id="dbt_debug",
        bash_command=(
            f"cd {DBT_PROJECT_DIR} && "
            f"dbt debug --profiles-dir {DBT_PROFILES_DIR} --target prod"
        ),
    )

    dbt_deps = BashOperator(
        task_id="dbt_deps",
        bash_command=(
            f"cd {DBT_PROJECT_DIR} && "
            f"dbt deps --profiles-dir {DBT_PROFILES_DIR}"
        ),
    )

    dbt_run_staging = BashOperator(
        task_id="dbt_run_staging",
        bash_command=(
            f"cd {DBT_PROJECT_DIR} && "
            f"dbt run --select staging --profiles-dir {DBT_PROFILES_DIR} --target prod --full-refresh"
        ),
    )

    dbt_run_marts = BashOperator(
        task_id="dbt_run_marts",
        bash_command=(
            f"cd {DBT_PROJECT_DIR} && "
            f"dbt run --select marts --profiles-dir {DBT_PROFILES_DIR} --target prod --full-refresh"
        ),
    )

    dbt_run_metrics = BashOperator(
        task_id="dbt_run_metrics",
        bash_command=(
            f"cd {DBT_PROJECT_DIR} && "
            f"dbt run --select metrics --profiles-dir {DBT_PROFILES_DIR} --target prod --full-refresh"
        ),
    )

    dbt_test = BashOperator(
        task_id="dbt_test",
        bash_command=(
            f"cd {DBT_PROJECT_DIR} && "
            f"dbt test --profiles-dir {DBT_PROFILES_DIR} --target prod"
        ),
    )

    dbt_docs_generate = BashOperator(
        task_id="dbt_docs_generate",
        bash_command=(
            f"cd {DBT_PROJECT_DIR} && "
            f"dbt docs generate --profiles-dir {DBT_PROFILES_DIR} --target prod"
        ),
    )

    # DAG dependency chain
    dbt_debug >> dbt_deps >> dbt_run_staging >> dbt_run_marts >> dbt_run_metrics >> dbt_test >> dbt_docs_generate