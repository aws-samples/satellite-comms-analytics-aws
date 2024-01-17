## Satellite communications capacity data generation for Amazon SageMaker Autopilot Timeseries

### Description
This Lambda function generates a sample Satellite Communications dataset for use in 
Capacity Forecasting scenarios with Amazon SageMaker Autopilot Timeseries. The associated blog 
is [here](https://aws.amazon.com/blogs/publicsector/maximizing-satellite-communications-usage-with-amazon-forecast/).

**Setup** - the user must specify an S3 bucket for the generated data. 

Sample CSV files are generated via the [satcom timeseries generation function](./lambda_function.py) 
with the following structure:

* timestamp (required, TimestampAttributeName)
* airpressure (covariate)
* beam (required: ItemIdentifierAttributeName)
* dayofweek (covariate)
* hourofday (covariate)
* mHz (required: TargetAttributeName)

IMPORTANT: When training a model, your input data can contain a mixture of covariate and static item metadata. 
Take care to create future-dated rows that extend to the end of your prediction horizon. In the future-dated rows, 
carry your static item metadata and expected covariate values. Future-dated target-value should be empty. 


### Example usage

* generate training data
Set the environment variables as follows

| Key      | Value       | Description |
| ---------| ----------- | ----------- |
| bucketName  | your-bucket-name-12345 | destination for the training data |
| timeseriesSatCom | satcom-autopilot-cap.csv | Satellite bandwidth usage and weather data |
| mode | train | generate training data |

mode can alternatively be set to 'inf' to generate a subset single item_id csv for Real Time Inference


### Configuration
The CloudFormation yaml will cover this however the key elements are: -
* permission to put objects to S3
* timeout extended to 60s

