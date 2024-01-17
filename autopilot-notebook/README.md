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




