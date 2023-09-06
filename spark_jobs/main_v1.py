
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

    # Step: Setting logger
    # Logging References
    # ref: https://polarpersonal.medium.com/writing-pyspark-logs-in-apache-spark-and-databricks-8590c28d1d51
    # ref: https://stackoverflow.com/questions/37291690/pyspark-logging
    log4j_logger = spark._jvm.org.apache.log4j
    LOGGER = log4j_logger.LogManager.getLogger(__name__)

    LOGGER.info("works!!")

if __name__ == "__main__":
    # convert positional args to kwargs
    kwargs = dict(zip(["job_name"], sys.argv[1:]))
    run(kwargs)
