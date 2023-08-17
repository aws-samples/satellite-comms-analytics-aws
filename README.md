## Predicting satellite communications capacity with Amazon Forecast

### Description
This repository contains sample code to demonstrate Satellite Communications Forecasting use-cases.

It focuses on a Maritime shipping use-case, using [Amazon Forecast](https://aws.amazon.com/forecast/) to build a time
series predictor model for each satellite beam in the ship(s) path, accounting for the impact of weather
conditions in a given location. It then renders results in [Amazon QuickSight](https://aws.amazon.com/quicksight/) BI tooling, displaying
forecasted capacity needs, accuracy metrics, and which attributes most impact the model.

![Capture_fig1](https://github.com/aws-samples/satellite-comms-forecast-aws/assets/122999933/d0769364-7bff-44cf-8cae-bf33319e1250)

Multiple factors such as weather and the geographical location of the vessel in the beam impact data rates and therefore the 
usage of satellite capacity bandwidth. 

Satellite Operators would like advance notice of capacity needs to plan out allocation, enabling the most efficient distribution 
of satellite capacity. This is where Amazon Forecast provides great benefit. Forecast can predict future capacity needs per beam leveraging 
historical bandwidth usage data and related time series such as weather metrics.

An accurate forecasting strategy can lead to lower costs (less bandwidth waste), and higher passenger 
satisfaction (e.g. successful capacity handling of surges). 


### Data generation and import

The primary (TTS) time-series data set required to predict future satellite capacity bandwidth needs is historical usage across
each spot-beam over a period of time. 
Secondary datasets (RTS) are optional but serve to improve the model accuracy e.g. weather has a correlation with achievable data rates
hence supplying weather data points, particularly severe weather, helps the Predictor.

We supply 14 days of historical and related time series data at 10-minute intervals. Why do we need so much? 
In general the model accuracy improves with more data however more specifically we want to identify any 
day of week or hour of day patterns such as the daily sea breeze effect in summer in Florida, US. 

A [lambda function](satcom-forecast-datagen-fxn/lambda_function.py) is provided to generate the TTS and RTS datasets.
Surge capacity windows and severe weather troughs are applied to subsets of the data to validate that Forecast can
produce a model capable of handling typical SatCom scenarios such as congestion, ["rain fade"](https://en.wikipedia.org/wiki/Rain_fade) etc

The results in csv, are posted to [Amazon S3](https://aws.amazon.com/s3/). It is suggested to create a folder structure similar to below. This enables 
the Forecast Dataset import jobs to target the specific set of TTS or RTS files.
- satcom-forecast-bkt-12345/
  - dataset/
    - tts/
    - rts/
  
An [additional lambda function](noaa-ndbc-weather-fxn/lambda_function.py) is also provided to parse National Oceanic and Atmospheric Administration [National Data Buoy Center](https://www.ndbc.noaa.gov/) 
historical and real-time datasets e.g. [Station 41043](https://www.ndbc.noaa.gov/data/realtime2/41043.txt)


## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This library is licensed under the MIT-0 License. See the LICENSE file.

