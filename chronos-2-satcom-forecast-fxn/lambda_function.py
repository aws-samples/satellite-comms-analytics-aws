# /// script
# requires-python = ">=3.11,<3.12"
# dependencies = [
#   "boto3",
#   "pandas<3",
#   "numpy<2.2",
# ]
# ///

import json
import boto3
import pandas as pd
from io import StringIO

s3 = boto3.client("s3")
sagemaker_runtime = boto3.client("sagemaker-runtime")


def convert_df_to_payload(
    train_df: pd.DataFrame,
    test_df: pd.DataFrame | None = None,
    prediction_length: int = 1,
    target: str = "target",
    id_column: str = "item_id",
    timestamp_column: str = "timestamp",
    freq: str | None = None,
    quantile_levels: list[float] | None = None,
):
    """
    Converts past and future DataFrames into JSON payload format for the Chronos 2 endpoint.

    Args:
        train_df: Historical data with target, timestamp_column, and id_column.
        test_df: Future covariates with timestamp_column and id_column.
        prediction_length: Number of future time steps to predict.
        target: Column name(s) for target values (str for univariate, list for multivariate).
        id_column: Column name for item IDs.
        timestamp_column: Column name for timestamps.
        freq: Optional Pandas-compatible frequency of the time series.

    Returns:
        dict: JSON payload formatted for the Chronos endpoint.
    """
    train_df[timestamp_column] = pd.to_datetime(train_df[timestamp_column])
    train_df = train_df.sort_values([id_column, timestamp_column])
    if test_df is not None:
        test_df[timestamp_column] = pd.to_datetime(test_df[timestamp_column])
        test_df = test_df.sort_values([id_column, timestamp_column])

    past_covariate_cols = list(
        train_df.columns.drop([target, id_column, timestamp_column])
    )
    future_covariate_cols = (
        []
        if test_df is None
        else [col for col in past_covariate_cols if col in test_df.columns]
    )

    inputs = []
    for item_id, past_group in train_df.groupby(id_column):
        target_values = past_group[target].tolist()
        series_length = len(target_values)

        if series_length < 5:
            raise ValueError(f"Time series '{item_id}' has fewer than 5 observations.")

        series_dict = {"target": target_values, "item_id": str(item_id)}

        if past_covariate_cols:
            series_dict["past_covariates"] = past_group[past_covariate_cols].to_dict(
                orient="list"
            )

        if future_covariate_cols:
            future_group = test_df[test_df[id_column] == item_id]
            if len(future_group) != prediction_length:
                raise ValueError(
                    f"test_df must contain exactly {prediction_length=} values for each item_id from train_df "
                    f"(got {len(future_group)=}) for {item_id=}"
                )
            series_dict["future_covariates"] = future_group[
                future_covariate_cols
            ].to_dict(orient="list")

        inputs.append(series_dict)

    parameters = {"prediction_length": prediction_length}
    if quantile_levels is not None:
        parameters["quantile_levels"] = quantile_levels
    return {"inputs": inputs, "parameters": parameters}


def lambda_handler(event, context):
    bucket = event["bucket"]
    train_key = event["train_key"]
    test_key = event["test_key"]
    endpoint_name = event["endpoint_name"]

    # Read CSV from S3
    train_obj = s3.get_object(Bucket=bucket, Key=train_key)
    train_df = pd.read_csv(StringIO(train_obj["Body"].read().decode("utf-8")))

    test_obj = s3.get_object(Bucket=bucket, Key=test_key)
    test_df = pd.read_csv(StringIO(test_obj["Body"].read().decode("utf-8")))

    prediction_length = len(test_df) // test_df["beam"].nunique()

    payload = convert_df_to_payload(
        train_df,
        test_df,
        prediction_length=prediction_length,
        id_column="beam",
        timestamp_column="timestamp",
        target="mHz",
        quantile_levels=[0.1, 0.5, 0.9],
    )

    # Invoke the endpoint
    try:
        response = sagemaker_runtime.invoke_endpoint(
            EndpointName=endpoint_name,
            ContentType="application/json",
            Body=json.dumps(payload),
        )

        # Parse the response
        result = json.loads(response["Body"].read().decode())
        print(f"Predicted Median for {result['predictions'][0]['item_id']}: {result['predictions'][0]['0.5']}")

        predictions = result["predictions"]

        return {"statusCode": 200, "body": json.dumps(result)}

    except Exception as e:
        print(f"Error invoking endpoint: {str(e)}")
        print("Please verify your endpoint configuration and payload format")


def main():
    event = {
        "bucket": "forecast-satcom-chronos2-capacity",
        "train_key": "dataset/satcom-chronos2-cap_train.csv",
        "test_key": "dataset/satcom-chronos2-cap_test.csv",
        "endpoint_name": "jumpstart-dft-pt-forecasting-chrono-20260216-185712",
    }
    print(json.dumps(lambda_handler(event, None), indent=2))


if __name__ == "__main__":
    main()
