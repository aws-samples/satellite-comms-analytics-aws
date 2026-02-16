import boto3
import json

# 1. Initialize the SageMaker Runtime client
runtime = boto3.client("sagemaker-runtime")

endpoint_name = "jumpstart-dft-pt-forecasting-chrono-20260205-202743"

# 2. Define your payload
# Chronos-2 expects 'inputs' as a list of dictionaries
payload = {
    "inputs": [
        {
            "target": [42.1, 45.3, 44.8, 46.2, 48.0],
            "item_id": "sensor_01"
        }
    ],
    "parameters": {
        "prediction_length": 5,
        "quantile_levels": [0.1, 0.5, 0.9]
    }
}

# 3. Invoke the endpoint
response = runtime.invoke_endpoint(
    EndpointName=endpoint_name,
    ContentType="application/json",
    Body=json.dumps(payload)
)

# 4. Parse the results
result = json.loads(response["Body"].read().decode())

# Accessing the first prediction in the batch
prediction = result["predictions"][0]
print(f"Mean Forecast: {prediction['mean']}")
print(f"P90 Forecast: {prediction['0.9']}")