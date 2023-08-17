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



## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This library is licensed under the MIT-0 License. See the LICENSE file.

