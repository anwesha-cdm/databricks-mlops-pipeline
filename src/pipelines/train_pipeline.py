# src/pipelines/train_pipeline.py

from pyspark.sql import SparkSession
from src.data.load_data import load_data, validate_data
from src.features.feature_engineering import (
    clean_data,
    create_features,
    add_primary_key
)


def run_pipeline(spark: SparkSession, data_path: str):
    """
    End-to-end training pipeline
    """

    # Step 1: Load
    df = load_data(spark, data_path)

    # Step 2: Validate
    validate_data(df)

    # Step 3: Clean
    df = clean_data(df)

    # Step 4: Feature engineering
    df = create_features(df)

    # Step 5: Add ID
    df = add_primary_key(df)

    return df