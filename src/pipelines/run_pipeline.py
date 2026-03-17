import sys
import os

project_root = "/Workspace/Users/shrivastavas@cdmsmith.com/.bundle/databricks-mlops-pipeline/dev/files"
sys.path.append(project_root)

import yaml
from pyspark.sql import SparkSession

from src.pipelines.train_pipeline import run_pipeline
from src.features.feature_store import create_feature_table
from src.training.train_model import train_model


def main():

    spark = SparkSession.builder.getOrCreate()

    config_path = os.path.join(project_root, "configs/config.yaml")

    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    df = run_pipeline(spark, config)

    create_feature_table(df, config)

    train_model(spark, config)


if __name__ == "__main__":
    main()