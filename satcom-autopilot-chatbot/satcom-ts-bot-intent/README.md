## Satellite communications capacity data generation for Amazon Forecast

### Description
This Lambda function generates a sample Satellite Communications dataset for use in 
Capacity Forecasting scenarios with Amazon Forecast. The associated blog 
is [here](https://aws.amazon.com/blogs/publicsector/maximizing-satellite-communications-usage-with-amazon-forecast/).

**Setup** - the user must specify an S3 bucket for the generated data. 

Sample CSV files are generated via the [satcom timeseries generation function](./lambda_function.py) 
with the following structure:

TTS - Target Time Series

* timestamp (required, TimestampAttributeName)
* mHz (required: TargetAttributeName)
* beam (required: ItemIdentifierAttributeName)

RTS - Related Time Series (covariates)
* timestamp (required, TimestampAttributeName)
* airpressure (covariate)
* beam (required: ItemIdentifierAttributeName)
* dayofweek (covariate)
* hourofday (covariate)

For best results, the covariate (airpressure) should be future-dated

### Example usage

* generate training data
Set the environment variables as follows

| Key      | Value       | Description |
| ---------| ----------- | ----------- |
| bucketName  | your-bucket-name-12345 | destination for the TTS and RTS data |
| ttsSatComUsage | satcom-cap.csv | Satellite bandwidth usage data |
| rtsWeather | maritime-weather.csv | Related Weather data |


### Configuration
The CloudFormation yaml will cover this however the key elements are: -
* permission to put objects to S3
* timeout extended to at least 30s

