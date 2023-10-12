
from datetime import datetime, timedelta

from airflow import DAG

from airflow.operators.python import PythonOperator
from airflow.hooks.S3_hook import S3Hook
from helper import scrap_cars_data, local_to_s3



with DAG(
    # These args will get passed on to each operator
    # You can override them on a per-task basis during operator initialization
    dag_id='scraper',
    description="cars data scraping",
    schedule_interval='@daily',
    start_date= datetime.now(),
    catchup=False,
    default_args={'provide_context': True}

    
) as dag:
    

    bucket_name = 'used-cars-egypt-data'

    load = PythonOperator(
            task_id = 'scrap',
            python_callable= scrap_cars_data
    )

   
    to_s3 = PythonOperator(
            task_id = 's3',
            python_callable= local_to_s3,
            op_args={
                bucket_name:bucket_name,
            }
    )
