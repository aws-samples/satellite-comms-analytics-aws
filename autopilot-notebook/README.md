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

**Setup** - the user must specify an S3 bucket for the input data. The main input is the 
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


**Model Training** - we create an auto ML job of type timeseries forecast using the API 
[create_auto_ml_job_v2](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sagemaker/client/create_auto_ml_job_v2.html)

The configuration is important: -
* set the forecast frequency - we use 10min intervals
* specify the horizon - we use 144 (1 day : 6 * 24)
* indicate which quantiles to predict - p70, p90 is useful in Sat Capacity forecasting to slightly overprovision.
* set the target attribute, timestamp & item_id attributes
 
Training can take 1-2 hours, at the end of which the best candidate model from the AutoPredictor is printed.


**Real Time Inference** - using the best candidate model we create an endpoint to run inferences against. 

A small, sample CSV with the same schema as the training dataset is supplied narrowed down to the item_id(s) of interest.

Invoking the endpoint is quick (< 60 secs).

The real-time predictions are saved in the S3 bucket.


**Clean-up** - As needed, you can stop the endpoint and related billing costs as follows. 
When you need the endpoint again, you can follow the deployment steps again. 
Ideally, at a future time, another newer model is trained and able to be deployed as well.



