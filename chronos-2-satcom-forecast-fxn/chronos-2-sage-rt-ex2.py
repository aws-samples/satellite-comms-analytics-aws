import boto3
import json

runtime = boto3.client("sagemaker-runtime")
endpoint_name = "jumpstart-dft-pt-forecasting-chrono-20260205-202743"

# 1. Define your historical data
# Length is 6
history_target = [120, 125, 118, 130, 135, 140]

# Past covariates MUST be the same length (6)
historical_temp = [72, 75, 71, 78, 80, 82]
historical_foot_traffic = [500, 520, 480, 550, 590, 610]

# 2. Construct the payload
payload = {
    "inputs": [
        {
            "target": history_target,
            "item_id": "store_01",
            "past_covariates": {
                "temperature": historical_temp,
                "foot_traffic": historical_foot_traffic
            }
        }
    ],
    "parameters": {
        "prediction_length": 3,  # Forecasting the next 3 steps
        "quantile_levels": [0.5]
    }
}

# 3. Invoke and Parse
response = runtime.invoke_endpoint(
    EndpointName=endpoint_name,
    ContentType="application/json",
    Body=json.dumps(payload)
)

result = json.loads(response["Body"].read().decode())
print(f"Predicted Median: {result['predictions'][0]['0.5']}")