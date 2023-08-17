## Predicting satellite communications capacity with Amazon Forecast

### Description
This repository contains sample code to demonstrate Satellite Communications Forecasting use-cases.

It focuses on a Maritime shipping use-case, using [Amazon Forecast](https://aws.amazon.com/forecast/) to build a time
series predictor model for each satellite beam in the ship(s) path, accounting for the impact of weather
conditions in a given location. It then renders results in Amazon QuickSight BI tooling, displaying
forecasted capacity needs, accuracy metrics, and which attributes most impact the model.

![Capture_fig1](https://github.com/aws-samples/satellite-comms-forecast-aws/assets/122999933/d0769364-7bff-44cf-8cae-bf33319e1250)

Multiple factors such as weather and the geographical location of the vessel in the beam impact data rates and therefore the 
usage of satellite capacity bandwidth. 

Satellite Operators would like advance notice of capacity needs to plan out allocation, enabling the most efficient distribution 
of satellite capacity. This is where Amazon Forecast provides great benefit. Forecast can predict future capacity needs per beam leveraging 
historical bandwidth usage data and related time series such as weather metrics.

An accurate forecasting strategy can lead to lower costs (less bandwidth waste), and higher passenger 
satisfaction (e.g. successful capacity handling of surges). 


## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This library is licensed under the MIT-0 License. See the LICENSE file.

