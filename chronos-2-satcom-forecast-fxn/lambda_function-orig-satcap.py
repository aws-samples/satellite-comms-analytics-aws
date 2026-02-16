import json
import boto3
import pandas as pd
from io import StringIO

s3 = boto3.client('s3')
sagemaker_runtime = boto3.client('sagemaker-runtime')


def lambda_handler(event, context):
    bucket = event['bucket']
    train_key = event['train_key']
    test_key = event['test_key']
    endpoint_name = event['endpoint_name']
    
    # Read CSV from S3
    train_obj = s3.get_object(Bucket=bucket, Key=train_key)
    train_df = pd.read_csv(StringIO(train_obj['Body'].read().decode('utf-8')))
    
    test_obj = s3.get_object(Bucket=bucket, Key=test_key)
    test_df = pd.read_csv(StringIO(test_obj['Body'].read().decode('utf-8')))

    # Parse timestamp column
    train_df['timestamp'] = pd.to_datetime(train_df['timestamp'])

    # Extract target variable (mHz)
    time_series_data = train_df['mHz'].tolist()

    # Extract covariates
    airpressure = train_df['airpressure'].tolist()
    beam = train_df['beam'].tolist()
    dayofweek = train_df['dayofweek'].tolist()
    hourofday = train_df['hourofday'].tolist()

    # Extract future covariates eg weather forecast
    airpressure_fut = test_df['airpressure'].tolist()

    # Determine prediction length
    prediction_length = 12  # Adjust as needed

    # Construct the payload
    payload = {
        "inputs": [
            {
                "target": time_series_data,
                "item_id": "SpotH3",
                "past_covariates": {
                    "airpressure": airpressure,
                    "beam": beam,
                    "dayofweek": dayofweek,
                    "hourofday": hourofday
                },
                "future_covariates": {
                    "airpressure": airpressure_fut
                }
            }
        ],
        "parameters": {
            "prediction_length": prediction_length,  # Forecasting the next N steps
            "quantile_levels": [0.1, 0.5, 0.9]
        }
    }

    # Invoke the endpoint
    try:
        response = sagemaker_runtime.invoke_endpoint(
            EndpointName=endpoint_name,
            ContentType='application/json',
            Body=json.dumps(payload)
        )

        # Parse the response
        result = json.loads(response["Body"].read().decode())
        print(f"Predicted Median: {result['predictions'][0]['0.5']}")

        predictions = result['predictions']

        return {'statusCode': 200, 'body': json.dumps(result)}

    except Exception as e:
        print(f"Error invoking endpoint: {str(e)}")
        print("Please verify your endpoint configuration and payload format")




def main():
    event = {
        "bucket": "forecast-satcom-chronos2-capacity",
        "train_key": "dataset/satcom-chronos2-cap_train-small.csv",
        "test_key": "dataset/satcom-chronos2-cap_test-small.csv",
        "endpoint_name": "jumpstart-dft-pt-forecasting-chrono-20260205-202743"
    }
    print(json.dumps(lambda_handler(event, None), indent=2))

if __name__ == '__main__':
    main()
