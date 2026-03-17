# src/features/feature_store.py

from databricks.feature_store import FeatureStoreClient
from pyspark.sql import DataFrame


def create_feature_table(df: DataFrame, table_name: str):
    """
    Create feature store table
    """

    fs = FeatureStoreClient()

    fs.create_table(
        name=table_name,
        primary_keys=["id"],
        df=df,
        description="Water quality engineered features"
    )


def read_feature_table(table_name: str):
    """
    Read feature store table
    """

    fs = FeatureStoreClient()

    return fs.read_table(table_name)