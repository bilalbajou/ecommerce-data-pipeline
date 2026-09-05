import os
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator

# Base command to run scripts within the isolated virtual environment
PYTHON_EXECUTABLE = "/opt/airflow/etl_venv/bin/python"

default_args = {
    'owner': 'data_engineer',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    # Configure retries and retry delays
    'retries': 3,
    'retry_delay': timedelta(minutes=2),
}

with DAG(
    'ecommerce_daily_etl',
    default_args=default_args,
    description='Daily ETL pipeline for E-commerce data',
    schedule_interval='*/2 * * * *',
    start_date=datetime(2023, 1, 1),
    catchup=False,
    tags=['ecommerce', 'etl'],
    doc_md="""
# E-commerce Data Pipeline
This DAG orchestrates the daily ingestion of e-commerce data.
It strictly follows the sequence: **Extract** -> **Transform** -> **Load** -> **Validate**.
    """
) as dag:

    extract_task = BashOperator(
        task_id='extract_data',
        bash_command=f'{PYTHON_EXECUTABLE} -m src.extract',
        env={**os.environ},
        cwd='/opt/airflow',
        execution_timeout=timedelta(minutes=15),
        doc_md="Extracts raw data from the external API and saves it locally."
    )

    transform_task = BashOperator(
        task_id='transform_data',
        bash_command=f'{PYTHON_EXECUTABLE} -m src.transform',
        env={**os.environ},
        cwd='/opt/airflow',
        execution_timeout=timedelta(minutes=10),
        doc_md="Cleanses the raw data, applies business logic, and standardizes formats."
    )

    load_task = BashOperator(
        task_id='load_data',
        bash_command=f'{PYTHON_EXECUTABLE} -m src.load',
        env={**os.environ},
        cwd='/opt/airflow',
        execution_timeout=timedelta(minutes=20),
        doc_md="Incrementally upserts the transformed data into the PostgreSQL database."
    )

    validate_task = BashOperator(
        task_id='validate_data',
        bash_command=f'{PYTHON_EXECUTABLE} -m src.validate',
        env={**os.environ},
        cwd='/opt/airflow',
        execution_timeout=timedelta(minutes=5),
        doc_md="Runs strict data quality constraints against the database as the final gate."
    )

    # Explicit Task Dependencies
    extract_task >> transform_task >> load_task >> validate_task
