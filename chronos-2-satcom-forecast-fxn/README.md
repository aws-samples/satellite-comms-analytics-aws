# Chronos-2 Satellite Capacity Forecasting

This solution provides time series forecasting for satellite capacity using Amazon SageMaker's Chronos-2 TimeSeries Foundational Model, AWS Lambda for 
inference orchestration, and a Streamlit UI for capacity predictions visualization.

## Architecture

- **SageMaker Endpoint**: Hosts the Chronos-2 foundation model for time series forecasting
- **Lambda Function**: Orchestrates data loading from S3 and invokes the SageMaker endpoint
- **Streamlit UI**: Interactive web interface for generating and visualizing forecasts

![Streamlit UI of satellite capacity forecasting](images/Screenshot%202026-02-16%20144116.png)


## Prerequisites

- AWS Account with appropriate permissions
- AWS CLI configured
- Python 3.12
- S3 bucket for training/test data and Lambda deployment package

## Deployment

### 1. Deploy Chronos-2 SageMaker Endpoint

1. Navigate to the [SageMaker Console](https://console.aws.amazon.com/sagemaker/)
2. Go to **Inference** > **Models** > **Create model**
3. Search for "Chronos-2" in the AWS Marketplace or JumpStart models
4. Select the Chronos-2 model and click **Deploy**
5. Configure the endpoint:
   - Instance type: `ml.g5.xlarge` or larger
   - Endpoint name: Note this for later use
6. Wait for deployment to complete (5-10 minutes)

### 2. Package and Upload Lambda Code

```bash
# Create deployment package
zip lambda-function.zip lambda_function.py

# Upload to S3
aws s3 cp lambda-function.zip s3://YOUR-BUCKET/lambda-function.zip
```

### 3. Deploy Lambda Function

```bash
aws cloudformation deploy \
  --template-file chronos-2-satcom-forecast-cfn.yaml \
  --stack-name satcom-forecast-lambda \
  --parameter-overrides \
      S3Bucket=YOUR-BUCKET \
      S3Key=lambda-function.zip \
  --capabilities CAPABILITY_IAM
```

### 4. Configure Streamlit Application

Edit `environment_variables.sh`:

```bash
export ENDPOINT_NAME="your-chronos-endpoint-name"
export LAMBDA_FUNCTION_NAME="satcom-chronos-forecast"
export AWS_REGION="us-east-1"
```

Install dependencies and run:

```bash
pip install streamlit boto3 pandas matplotlib

source environment_variables.sh
streamlit run app.py
```

## Usage

### Lambda Function

The Lambda function accepts the following input:

```json
{
  "bucket": "forecast-satcom-chronos2-capacity",
  "train_key": "train_data.csv",
  "test_key": "test_data.csv",
  "endpoint_name": "chronos-endpoint-name"
}
```

**Invoke via AWS CLI:**

```bash
aws lambda invoke \
  --function-name satcom-chronos-forecast \
  --payload '{"bucket":"YOUR-BUCKET","train_key":"train.csv","test_key":"test.csv","endpoint_name":"YOUR-ENDPOINT"}' \
  response.json
```

**Response format:**

```json
{
  "statusCode": 200,
  "body": "{\"predictions\": [{\"item_id\": \"SpotH12\", \"0.1\": [...], \"0.5\": [...], \"0.9\": [...]}]}"
}
```

The function:
1. Loads training and test data from S3
2. Calculates prediction length based on test data
3. Converts data to Chronos-2 payload format
4. Invokes the SageMaker endpoint
5. Returns predictions with quantiles (0.1, 0.5, 0.9)

### Streamlit UI

The web interface provides:

1. **S3 Bucket Name**: Text input (default: `forecast-satcom-chronos2-capacity`)
2. **Training Data**: Dropdown to select training data CSV file from S3
3. **Test Data**: Dropdown to select test data CSV file from S3
4. **Item ID**: Dropdown to select which time series to visualize
5. **Generate Forecast**: Button to invoke Lambda and display results

**Output:**
- Median forecast values (0.5 quantile)
- Interactive plot showing:
  - Historical data (blue)
  - Ground truth (green)
  - Forecast (violet)
  - Prediction interval (shaded area between 0.1 and 0.9 quantiles)

**Customization:**

Modify `environment_variables.sh` to change:
- `ENDPOINT_NAME`: SageMaker endpoint to use
- `LAMBDA_FUNCTION_NAME`: Lambda function to invoke
- `AWS_REGION`: AWS region for resources

Change the bucket name in the UI text input or modify the default in `app.py`.

## Data Format

For consistency uses the same data format as the original ML-based SageMaker Autopilot timeseries
predictions. See [this README for details](../satcom-timeseries-autopilot-gen-fxn/README.md)

**Training Data (CSV):**
```csv
timestamp,airpressure,beam,dayofweek,hourofday,mHz
2023-06-12 00:00:00,1011,SpotH3,0,0,212.0
2023-06-12 00:00:00,1046,SpotH7,0,0,284.0
2023-06-12 00:00:00,1030,SpotH12,0,0,204.0
2023-06-12 00:00:00,1012,SpotH15,0,0,249.0
2023-06-12 00:10:00,1032,SpotH3,0,0,218.0
```

**Test Data (CSV):**
```csv
timestamp,airpressure,beam,dayofweek,hourofday,mHz
2023-06-13 00:00:00,1029,SpotH3,1,0,206.0
2023-06-13 00:00:00,1050,SpotH7,1,0,259.0
2023-06-13 00:00:00,1022,SpotH12,1,0,211.0
```

Required columns:
- `beam`: Time series identifier
- `timestamp`: Datetime in format `YYYY-MM-DD HH:MM:SS`
- `mHz`: Target variable (capacity in MHz)

Covariates: 
- `airpressure`: NOAA buoy airpressure readings
- `dayofweek`: 0-6 (not necessary for Chronos-2 since the model can infer this)
- `hourofday`: 0-23 (not necessary for Chronos-2 since the model can infer this)

You can add many more covariates to your forecasting model.

## Teardown

### Delete Lambda Function

```bash
aws cloudformation delete-stack --stack-name satcom-forecast-lambda
```

### Delete SageMaker Endpoint

```bash
aws sagemaker delete-endpoint --endpoint-name YOUR-ENDPOINT-NAME
aws sagemaker delete-endpoint-config --endpoint-config-name YOUR-ENDPOINT-CONFIG-NAME
aws sagemaker delete-model --model-name YOUR-MODEL-NAME
```

Or via the SageMaker Console:
1. Go to **Inference** > **Endpoints**
2. Select your endpoint and click **Delete**
3. Confirm deletion of associated endpoint configuration and model

### Clean Up S3 Data

```bash
aws s3 rm s3://YOUR-BUCKET/lambda-function.zip
aws s3 rm s3://YOUR-BUCKET/train.csv
aws s3 rm s3://YOUR-BUCKET/test.csv
```

## Troubleshooting

**Lambda timeout errors**: Increase timeout in CloudFormation template (currently 60 seconds)

**Endpoint not found**: Verify endpoint name in `environment_variables.sh` matches deployed endpoint

**S3 access denied**: Ensure Lambda IAM role has `s3:GetObject` permissions for your bucket

**Streamlit connection errors**: Check AWS credentials are configured (`aws configure`)

## Cost Considerations

- **SageMaker Endpoint**: Charges per hour while running (~$1-2/hour for ml.g5.xlarge)
- **Lambda**: Pay per invocation and execution time
- **S3**: Storage and data transfer costs

Delete the SageMaker endpoint when not in use to avoid ongoing charges.
