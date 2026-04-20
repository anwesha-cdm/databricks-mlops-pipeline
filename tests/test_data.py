from pyspark.sql import SparkSession
from src.data.load_data import load_data


def test_load_data():

    spark = SparkSession.builder.getOrCreate()

    config = {"data": {"input_path": "/FileStore/data/train.csv"}}

    df = load_data(spark, config)

    assert df.count() > 0