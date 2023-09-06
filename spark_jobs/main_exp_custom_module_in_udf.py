
import os
import sys

import pyspark
import pyspark.sql.functions as F
import pyspark.sql.types as T

# from pyspark.context import SparkContext
from pyspark.sql import (  # https://spark.apache.org/docs/latest/api/python/reference/api/pyspark.sql.SparkSession.html#pyspark.sql.SparkSession
    DataFrame,
    SparkSession,
)

from typing import Any, Dict

try:
    from spark_jobs.common_lib.hello_world import get_hostname
except:
    pass

@F.udf
def append_executor_hostname(v):

    # Added the `sleep` and multiple write to make sure the `emr-container-fluentd` stream the log to Log Storage.
    import time
    for _ in range(10):
        print(f"---> Executor: Python Import Path: {sys.path}")
        print(f"---> Executor: PYTHONPATH: {os.environ.get('PYTHONPATH')}")
        print(f"---> Executor: Python Current Path: {os.getcwd()}")
        print(f"---> Executor: Python Files in . Path: {os.listdir('.')}")
        print(f"---> Executor: Python Files in /home/hadoop Path: {os.listdir('/home/hadoop')}")
        print(f"---> Executor: Python Files in /my_src Path: {os.listdir('/my_src')}")
        exec_hostname = get_hostname()
        time.sleep(1)

    # exec_hostname = "dummy"
    return f"{v}-{exec_hostname}"

def run(kwargs: Dict[Any,Any]):

    os.environ["AWS_DEFAULT_REGION"] = "us-west-2"
    spark_sql_warehouse_location = os.path.abspath("spark-warehouse")

    spark = (
        SparkSession.builder.appName(f"{kwargs['job_name']}")
        .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer")
        # @deprecated: 2022-04-04:  As of 0.9, https://aws.amazon.com/blogs/big-data/new-features-from-apache-hudi-0-9-0-on-amazon-emr/
        .config("spark.sql.hive.convertMetastoreParquet", "false")
        # ref: https://aws.github.io/aws-emr-containers-best-practices/metastore-integrations/docs/aws-glue/#sync-hudi-table-with-aws-glue-catalog
        .enableHiveSupport()  # the same as .config("spark.sql.catalogImplementation", "hive")
        .config("spark.sql.warehouse.dir", spark_sql_warehouse_location)
        .getOrCreate()
    )
    # This puts the custom python module /home/hadoop.
    spark.sparkContext.addPyFile("dependency_packages.zip")

    # Step: Setting logger
    # Logging References
    # ref: https://polarpersonal.medium.com/writing-pyspark-logs-in-apache-spark-and-databricks-8590c28d1d51
    # ref: https://stackoverflow.com/questions/37291690/pyspark-logging
    log4j_logger = spark._jvm.org.apache.log4j
    LOGGER = log4j_logger.LogManager.getLogger(__name__)

    LOGGER.info("works!!")
    LOGGER.info(f"===> Python Import Path: {sys.path}")
    LOGGER.info(f"===> Python PYTHONPATH: {os.environ.get('PYTHONPATH')}")
    LOGGER.info(f"===> Python Current Path: {os.getcwd()}")
    LOGGER.info(f"===> Python Files in . Path: {os.listdir('.')}")
    LOGGER.info(f"===> Python Files in /home/hadoop Path: {os.listdir('/home/hadoop')}")

    from spark_jobs.common_lib.hello_world import get_hostname
    spark_driver_hostname = get_hostname()
    LOGGER.info(f"===> Spark Driver Hostname: {spark_driver_hostname}")

    df = spark.createDataFrame([[11,"moon","lee"], [22,"gatsby","lee"]], ['age','fname','lname'])
    df_transformed = df.withColumn(
        "exec_hostname",
        append_executor_hostname(F.col("age")),
    )
    df_transformed.printSchema(); df_transformed.show(truncate=False)  # fmt: skip

if __name__ == "__main__":
    # convert positional args to kwargs
    kwargs = dict(zip(["job_name"], sys.argv[1:]))
    run(kwargs)
