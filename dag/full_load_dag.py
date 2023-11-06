
from datetime import datetime

from airflow.decorators import dag

from helpers import scrap_cars_data, local_to_s3, scrap_cars_body, local_to_s3
from airflow.providers.amazon.aws.operators.redshift_data import RedshiftDataOperator
from airflow.providers.amazon.aws.transfers.s3_to_redshift import  S3ToRedshiftOperator
from airflow.decorators import task




@dag(
    dag_id='full_load',
    description="cars data scraping",
    max_active_runs=1,
    schedule='@once',
    start_date= datetime.now(),
    catchup=False,
)
def full_load_pipeline():
    AWS_CONN_ID='aws-connection'
    S3_BUCKET_NAME = 'used-cars-egypt-data'


    scrap_data = scrap_cars_data.override(task_id='scrap_cars_data')()

    local_data_to_s3 = local_to_s3.override(task_id='cars_data_to_s3')(S3_BUCKET_NAME, scrap_data)

    scrap_body_data = scrap_cars_body.override(task_id='scrap_cars_body_data')()
    
    local_body_data_to_s3 = local_to_s3.override(task_id='cars_body_data_to_s3')(S3_BUCKET_NAME, scrap_body_data)

    db_init = RedshiftDataOperator(
        task_id='create_redshift_table_schemas',
        database='cars',
        sql='sql/init_db_schema.sql',
        cluster_identifier='cars-data',
        db_user='aya',
        aws_conn_id=AWS_CONN_ID,
    )


    cars_s3_to_redshift = S3ToRedshiftOperator(
            task_id="transfer_s3_to_redshift",
            redshift_conn_id='redshift-cluster',
            s3_bucket=S3_BUCKET_NAME,
            s3_key=local_data_to_s3,
            schema="raw_schema",
            table='cars_data',
            aws_conn_id = AWS_CONN_ID,
            copy_options=['csv',"IGNOREHEADER 1"],

        )

    cars_body_s3_to_redshift = S3ToRedshiftOperator(
            task_id="transfer_body_s3_to_redshift",
            redshift_conn_id='redshift-cluster',
            s3_bucket=S3_BUCKET_NAME,
            s3_key=local_body_data_to_s3,
            schema="raw_schema",
            table='cars_body_data',
            aws_conn_id = AWS_CONN_ID,
            copy_options=['csv',"IGNOREHEADER 1"],
        )
    
    full_load = RedshiftDataOperator(
        task_id='production_db_full_load',
        database='cars',
        sql='sql/full_load.sql',
        cluster_identifier='cars-cluster',
        db_user='aya',
        aws_conn_id=AWS_CONN_ID,
        
    )
    db_init >> cars_s3_to_redshift >> cars_body_s3_to_redshift >> full_load
    
full_load_pipeline()

