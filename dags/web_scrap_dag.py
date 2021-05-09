from datetime import timedelta
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.utils.dates import days_ago

from web_scrap import scrapping_rentals_ca

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': days_ago(0,0,0,0,0),
    'email': ['lianjjchina@hotmail.com'],
    'email_on_failure': False,
    "retries": 1
}

dag = DAG(
        dag_id="rental_price",
        default_args= default_args,
        schedule_interval=timedelta(days = 1),
)


run_etl = PythonOperator(
    task_id='web_scrap',
    python_callable=scrapping_rentals_ca,
    dag=dag,
)

run_etl