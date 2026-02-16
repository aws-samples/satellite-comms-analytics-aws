import streamlit as st
import boto3
import json
import os
import pandas as pd
import matplotlib.pyplot as plt
from io import StringIO

st.title("Satellite Capacity Forecast")

def plot_forecast(
    context_df: pd.DataFrame,
    pred_df: pd.DataFrame,
    test_df: pd.DataFrame,
    target_column: str,
    timeseries_id: str,
    id_column: str,
    timestamp_column: str = "timestamp",
    history_length: int = 512,
):
    ts_context = context_df.query(f"{id_column} == @timeseries_id").set_index(timestamp_column)[target_column]
    ts_pred = pred_df.query(f"{id_column} == @timeseries_id and target_name == @target_column").set_index(
        timestamp_column
    )[["0.1", "predictions", "0.9"]]
    ts_ground_truth = test_df.query(f"{id_column} == @timeseries_id").set_index(timestamp_column)[target_column]

    last_date = ts_context.index.max()
    start_idx = max(0, len(ts_context) - history_length)
    plot_cutoff = ts_context.index[start_idx]
    ts_context = ts_context[ts_context.index >= plot_cutoff]
    ts_pred = ts_pred[ts_pred.index >= plot_cutoff]
    ts_ground_truth = ts_ground_truth[ts_ground_truth.index >= plot_cutoff]

    fig = plt.figure(figsize=(12, 3))
    ax = fig.gca()
    ts_context.plot(ax=ax, label=f"historical {target_column}", color="xkcd:azure")
    ts_ground_truth.plot(ax=ax, label=f"future {target_column} (ground truth)", color="xkcd:grass green")
    ts_pred["predictions"].plot(ax=ax, label="forecast", color="xkcd:violet")
    ax.fill_between(
        ts_pred.index,
        ts_pred["0.1"],
        ts_pred["0.9"],
        alpha=0.7,
        label="prediction interval",
        color="xkcd:light lavender",
    )
    ax.axvline(x=last_date, color="black", linestyle="--", alpha=0.5)
    ax.legend(loc="upper left")
    ax.set_title(f"{target_column} forecast for {timeseries_id}")
    return fig


bucket_name = st.text_input("S3 Bucket Name", value="forecast-satcom-chronos2-capacity")

s3 = boto3.client("s3", region_name=os.environ["AWS_REGION"])
objects = s3.list_objects_v2(Bucket=bucket_name).get("Contents", [])
csv_files = [obj["Key"] for obj in objects if obj["Key"].endswith(".csv")]

train_file = st.selectbox("Training Data", csv_files)
test_file = st.selectbox("Test Data", csv_files)

# Load training data to get unique item_ids
if train_file:
    train_obj = s3.get_object(Bucket=bucket_name, Key=train_file)
    train_preview = pd.read_csv(StringIO(train_obj["Body"].read().decode("utf-8")))
    item_ids = train_preview["beam"].unique().tolist()
    selected_item_id = st.selectbox("Item ID", item_ids, index=0)

endpoint_name = os.environ["ENDPOINT_NAME"]

if st.button("Generate Forecast"):
    lambda_client = boto3.client("lambda", region_name=os.environ["AWS_REGION"])
    
    payload = {
        "bucket": bucket_name,
        "train_key": train_file,
        "test_key": test_file,
        "endpoint_name": endpoint_name
    }
    
    response = lambda_client.invoke(
        FunctionName=os.environ["LAMBDA_FUNCTION_NAME"],
        InvocationType="RequestResponse",
        Payload=json.dumps(payload)
    )
    
    result = json.loads(response["Payload"].read())
    predictions = json.loads(result["body"])["predictions"]

    # Find prediction for selected item_id
    selected_pred = next((p for p in predictions if p["item_id"] == selected_item_id), predictions[0])
    median_forecast = selected_pred["0.5"]
    
    st.subheader(f"Median Forecast (0.5 quantile) for {selected_item_id}")
    st.write(median_forecast)
    
    # Load data for plotting
    train_obj = s3.get_object(Bucket=bucket_name, Key=train_file)
    train_df = pd.read_csv(StringIO(train_obj["Body"].read().decode("utf-8")))
    test_obj = s3.get_object(Bucket=bucket_name, Key=test_file)
    test_df = pd.read_csv(StringIO(test_obj["Body"].read().decode("utf-8")))
    
    # Convert predictions to DataFrame
    pred_data = []
    for pred in predictions:
        for i, (q1, q5, q9) in enumerate(zip(pred["0.1"], pred["0.5"], pred["0.9"])):
            pred_data.append({
                "beam": pred["item_id"],
                "timestamp": test_df[test_df["beam"] == pred["item_id"]].iloc[i]["timestamp"],
                "target_name": "mHz",
                "0.1": q1,
                "predictions": q5,
                "0.9": q9
            })
    pred_df = pd.DataFrame(pred_data)
    pred_df["timestamp"] = pd.to_datetime(pred_df["timestamp"])
    train_df["timestamp"] = pd.to_datetime(train_df["timestamp"])
    test_df["timestamp"] = pd.to_datetime(test_df["timestamp"])
    
    # Plot forecast
    fig = plot_forecast(
        train_df, pred_df, test_df,
        target_column="mHz",
        timeseries_id=selected_item_id,
        id_column="beam",
        timestamp_column="timestamp"
    )
    st.pyplot(fig)
