# src/features/feature_engineering.py

from pyspark.sql import DataFrame
from pyspark.sql.functions import col, monotonically_increasing_id


def clean_data(df: DataFrame) -> DataFrame:
    """
    Handle missing values and duplicates
    """

    df = df.fillna(0)
    df = df.dropDuplicates()

    return df


def create_features(df: DataFrame) -> DataFrame:
    """
    Create meaningful features for model
    """

    df = df.withColumn(
        "ph_normalized", col("ph") / 14
    ).withColumn(
        "hardness_ratio", col("Hardness") / (col("Solids") + 1)
    ).withColumn(
        "organic_load", col("Organic_carbon") * col("Chloramines")
    )

    return df


def add_primary_key(df: DataFrame) -> DataFrame:
    """
    Add unique ID for feature store
    """

    df = df.withColumn("id", monotonically_increasing_id())

    return df