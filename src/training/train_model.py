import mlflow
import mlflow.sklearn

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

from src.features.feature_store import read_feature_table

from mlflow.models.signature import infer_signature


def train_model(spark, config):

    # Use Unity Catalog
    mlflow.set_registry_uri("databricks-uc")

    mlflow.set_experiment(config["mlflow"]["experiment_name"])

    env = config["env"]
    catalog = config["catalog"][env]

    # model config
    schema = config["model_registry"]["schema"]
    model_name = config["model_registry"]["name"]

    #  ensure schema exists
    # spark.sql(f"CREATE SCHEMA IF NOT EXISTS {catalog}.{schema}")

    # full UC model name
    full_model_name = f"{catalog}.{schema}.{model_name}"

    df = read_feature_table(config).toPandas()

    target = config["training"]["target"]

    X = df.drop(columns=[target])
    y = df[target]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=config["training"]["test_size"],
        random_state=config["training"]["random_state"]
    )

    with mlflow.start_run() as run:

        model = RandomForestClassifier(
            n_estimators=config["model"]["n_estimators"]
        )

        model.fit(X_train, y_train)

        preds = model.predict(X_test)
        acc = accuracy_score(y_test, preds)

        mlflow.log_metric("accuracy", acc)

        signature = infer_signature(X_train, model.predict(X_train))

        mlflow.sklearn.log_model(
                        model,
                        "model",
                        signature=signature,
                        input_example=X_train.iloc[:5]
                    )

        # REGISTER MODEL (FIXED)
        mlflow.register_model(
            f"runs:/{run.info.run_id}/model",
            full_model_name
        )