from pyspark.sql import SparkSession
from src.pipelines.train_pipeline import run_pipeline


def test_pipeline():

    spark = SparkSession.builder.getOrCreate()

    config = {"data": {"input_path": "/FileStore/data/train.csv"}}

    df = run_pipeline(spark, config)

    assert df.count() > 0
    assert "id" in df.columns