"""
Apache Airflow DAG - Customer Data Pipeline
Orchestrates daily ETL for customer data from multiple sources.
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.email import EmailOperator
from airflow.utils.dates import days_ago
import logging

logger = logging.getLogger(__name__)

default_args = {
    'owner': 'mansi-kamothi',
    'depends_on_past': False,
    'start_date': days_ago(1),
    'email': ['mansikamothi1999@gmail.com'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'customer_data_pipeline',
    default_args=default_args,
    description='Daily ETL pipeline for customer data',
    schedule_interval='0 6 * * *',  # Run at 6 AM daily
    catchup=False,
    tags=['etl', 'customers', 'daily'],
)


def extract_crm_data(**context):
    """Extract customer data from CRM system."""
    from src.extract import extract_from_crm
    logger.info("Extracting CRM data...")
    data = extract_from_crm()
    context['ti'].xcom_push(key='crm_record_count', value=len(data))
    logger.info(f"Extracted {len(data)} CRM records")
    return len(data)


def extract_event_data(**context):
    """Extract event data from analytics platform."""
    from src.extract import extract_events
    logger.info("Extracting event data...")
    data = extract_events()
    context['ti'].xcom_push(key='event_record_count', value=len(data))
    logger.info(f"Extracted {len(data)} event records")
    return len(data)


def validate_data(**context):
    """Validate data quality before loading."""
    from src.validate import run_validation_suite
    logger.info("Running data quality checks...")
    results = run_validation_suite()
    if not results['passed']:
        raise ValueError(f"Data validation failed: {results['failures']}")
    logger.info(f"All {results['checks_run']} validation checks passed!")
    return results


def transform_data(**context):
    """Transform and clean extracted data."""
    from src.transform import transform_customer_data
    logger.info("Transforming data...")
    stats = transform_customer_data()
    logger.info(f"Transformation complete: {stats}")
    return stats


def load_to_snowflake(**context):
    """Load transformed data to Snowflake."""
    from src.load import load_to_warehouse
    logger.info("Loading data to Snowflake...")
    result = load_to_warehouse()
    logger.info(f"Loaded {result['rows_inserted']} rows to Snowflake")
    return result


def run_dbt_models(**context):
    """Run dbt transformations after raw data load."""
    import subprocess
    logger.info("Running dbt models...")
    result = subprocess.run(
        ['dbt', 'run', '--select', 'staging.customers+'],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        raise RuntimeError(f"dbt run failed: {result.stderr}")
    logger.info("dbt models completed successfully")


def send_pipeline_report(**context):
    """Generate and send pipeline completion report."""
    crm_count = context['ti'].xcom_pull(key='crm_record_count', task_ids='extract_crm')
    event_count = context['ti'].xcom_pull(key='event_record_count', task_ids='extract_events')
    logger.info(f"Pipeline complete. CRM: {crm_count}, Events: {event_count}")


# Define tasks
extract_crm = PythonOperator(
    task_id='extract_crm',
    python_callable=extract_crm_data,
    dag=dag,
)

extract_events = PythonOperator(
    task_id='extract_events',
    python_callable=extract_event_data,
    dag=dag,
)

validate = PythonOperator(
    task_id='validate_data',
    python_callable=validate_data,
    dag=dag,
)

transform = PythonOperator(
    task_id='transform_data',
    python_callable=transform_data,
    dag=dag,
)

load = PythonOperator(
    task_id='load_to_snowflake',
    python_callable=load_to_snowflake,
    dag=dag,
)

dbt_run = PythonOperator(
    task_id='run_dbt_models',
    python_callable=run_dbt_models,
    dag=dag,
)

report = PythonOperator(
    task_id='send_report',
    python_callable=send_pipeline_report,
    dag=dag,
)

# Define task dependencies
[extract_crm, extract_events] >> validate >> transform >> load >> dbt_run >> report