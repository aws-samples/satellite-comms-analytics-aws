## Predicting satellite communications capacity with Amazon SageMaker Autopilot Timeseries

### Description
This notebook demonstrates a Satellite Communications Forecasting use-case leveraging
Amazon SageMaker Autopilot Timeseries, which in turn uses the same Ensembling and algorithms
as Amazon Forecast. The associated blog 
is [here](https://aws.amazon.com/blogs/publicsector/maximizing-satellite-communications-usage-with-amazon-forecast/).

The benefits of SageMaker Autopilot Timeseries over Amazon Forecast are: -
* accuracy metrics for all (6) algorithms leveraged in the AutoPredictor
* faster training time
* select which model to use (best candidate or otherwise)
* lower cost (particularly with Real Time Inference)

It is therefore recommended to use SageMaker Autopilot Timeseries over Amazon Forecast
for new prediction use-cases.


### Satellite Capacity SageMaker Autopilot Timeseries notebook workflow

A [Jupyter notebook](./satcom-autopilot-notebook.ipynb) is provided 
to automate the sequence of following events: -

Setup - the user must specify an S3 bucket for the input data. The main input is the 
training dataset which comprises of historical bandwidth usage, and weather data for a set
of Spot Beams (item_id's). One difference v Amazon Forecast is that all input data must be
combined into a single schema. 

1+ sample CSV files are generated via the [satcom timeseries generation function](../satcom-timeseries-autopilot-gen-fxn/lambda_function.py) 
with the following structure:

* timestamp (required, TimestampAttributeName)
* airpressure (covariate)
* beam (required: ItemIdentifierAttributeName)
* dayofweek (covariate)
* hourofday (covariate)
* mHz (required: TargetAttributeName)

IMPORTANT: When training a model, your input data can contain a mixture of covariate and static item metadata. 
Take care to create future-dated rows that extend to the end of your prediction horizon. In the future-dated rows, 
carry your static item metadata and expected covariate values. Future-dated target-value (y) should be empty. 




