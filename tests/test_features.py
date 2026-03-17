from pyspark.sql import SparkSession
from src.features.feature_engineering import create_features


def test_feature_creation():

    spark = SparkSession.builder.getOrCreate()

    data = [(7.0, 200.0, 10000.0, 10.0, 5.0)]
    cols = ["ph", "Hardness", "Solids", "Organic_carbon", "Chloramines"]

    df = spark.createDataFrame(data, cols)

    df = create_features(df)

    assert "ph_normalized" in df.columns
    assert "hardness_ratio" in df.columns
    assert "organic_load" in df.columns