
from datetime import datetime, timedelta

from airflow.decorators import dag

from helpers import scrap_cars_data, local_to_s3, scrap_cars_body, local_to_s3
from airflow.providers.amazon.aws.operators.redshift_data import RedshiftDataOperator
from airflow.providers.amazon.aws.transfers.s3_to_redshift import  S3ToRedshiftOperator


   
@dag(
    dag_id='incremental_load',
    description="cars data scraping",
    max_active_runs=1,
    schedule='@daily',
    start_date= datetime.now() + timedelta(days=1),
    catchup=False,
)
def incremental_cars_data_pipeline():

    s3_bucket_name = 'used-cars-egypt-data'

    scrap_data = scrap_cars_data.override(task_id='daily_scrap_cars_data')()

    local_data_to_s3 = local_to_s3.override(task_id='daily_cars_data_to_s3')(s3_bucket_name, scrap_data)

    scrap_body_data = scrap_cars_body.override(task_id='daily_scrap_cars_body_data')()
    
    local_body_data_to_s3 = local_to_s3.override(task_id='daily_cars_body_data_to_s3')(s3_bucket_name, scrap_body_data)



    truncate_tables =  RedshiftDataOperator(
        task_id='truncate_tables',
        database='cars',
        sql='sql/truncate.sql',
        cluster_identifier='cars-cluster',
        db_user='aya',
        aws_conn_id='aws-connection',
        
    )

    cars_s3_to_redshift = S3ToRedshiftOperator(
            task_id="daily_transfer_s3_to_redshift",
            redshift_conn_id='cars-redshift',
            s3_bucket=s3_bucket_name,
            s3_key=local_data_to_s3,
            schema="raw_schema",
            table='cars_data',
            aws_conn_id = 'aws-connection',
            copy_options=['csv',"IGNOREHEADER 1"],
        )

    cars_body_s3_to_redshift = S3ToRedshiftOperator(
            task_id="daily_trasnfer_body_s3_to_redshift",
            redshift_conn_id='cars-redshift',
            s3_bucket=s3_bucket_name,
            s3_key=local_body_data_to_s3,
            schema="raw_schema",
            table='cars_body_data',
            aws_conn_id = 'aws-connection',
            copy_options=['csv',"IGNOREHEADER 1"],
        )
    
    incremental_load = RedshiftDataOperator(
        task_id='production_db_incremental_load',
        database='cars',
        sql='sql/incremental_load.sql',
        cluster_identifier='cars-cluster',
        db_user='aya',
        aws_conn_id='aws-connection',
        
    )
    truncate_tables >> cars_s3_to_redshift >> cars_body_s3_to_redshift >> incremental_load

incremental_cars_data_pipeline()

