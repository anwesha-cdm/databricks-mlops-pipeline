# src/data/load_data.py

from pyspark.sql import SparkSession
from pyspark.sql import DataFrame



def load_data(spark: SparkSession, config: dict):
    """
    Load raw data from path
    """
    path = config["data"]["input_path"]

    df = spark.read.csv(path, header=True, inferSchema=True)

    return df


def validate_data(df: DataFrame) -> None:
    """
    Basic data validation checks
    """

    print("Schema:")
    df.printSchema()

    print("Null Counts:")
    from pyspark.sql.functions import col, count

    df.select([count(col(c)).alias(c) for c in df.columns]).show()

    print("Sample Data:")
    df.show(5)