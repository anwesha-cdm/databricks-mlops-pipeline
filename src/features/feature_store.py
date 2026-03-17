# # src/features/feature_store.py
# from databricks.feature_store import FeatureStoreClient
# from pyspark.sql import DataFrame


# def create_feature_table(df: DataFrame, config: dict):
#     """
#     Create or overwrite feature table
#     """

#     table_name = config["feature_store"]["table_name"]

#     fs = FeatureStoreClient()

#     try:
#         fs.write_table(
#             name=table_name,
#             df=df,
#             mode="overwrite"
#         )
#     except Exception:
#         fs.create_table(
#             name=table_name,
#             primary_keys=["id"],
#             df=df,
#             description="Water quality engineered features"
#         )


# def read_feature_table(config: dict):
#     """
#     Read feature table
#     """
#     table_name = config["feature_store"]["table_name"]

#     fs = FeatureStoreClient()

#     return fs.read_table(name=table_name)


from logging import config

from databricks.feature_store import FeatureStoreClient
from matplotlib.table import table


def create_feature_table(df, config):

    env = config["env"]
    catalog = config["catalog"][env]
    schema = config["feature_store"]["schema"]
    table = config["feature_store"]["table_name"]

    table_name = f"{catalog}.{schema}.{table}"

    fs = FeatureStoreClient()

    try:
        fs.write_table(name=table_name, df=df, mode="overwrite")
    except:
        fs.create_table(
            name=table_name,
            primary_keys=["id"],
            df=df,
            description="Water quality features"
        )


def read_feature_table(config):

    env = config["env"]
    catalog = config["catalog"][env]
    schema = config["feature_store"]["schema"]
    table = config["feature_store"]["table_name"]

    table_name = f"{catalog}.{schema}.{table}"

    fs = FeatureStoreClient()

    return fs.read_table(name=table_name)