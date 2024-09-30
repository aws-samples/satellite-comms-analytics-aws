## Satellite Capacity chatbot

### Description
The Satellite Capacity bot is a chatbot which either returns a satellite capacity forecast, or provides targeted responses 
to satellite related questions, depending on the user’s input questions. 

The bot is intended to show customers how they can (a) get inference results from a SageMaker endpoint in an
easy to use interface i.e. a chatbot, (b) integrate Bedrock Knowledgebase agents to existing applications to 
retrieve answers to domain-specific questions. 

This sub-project is associated with the blog [here](https://aws.amazon.com/blogs/publicsector/maximizing-satellite-communications-usage-with-amazon-forecast/).
It focuses on a Maritime shipping use-case, 
using [Amazon SageMaker Autopilot Timer-series](https://docs.aws.amazon.com/sagemaker/latest/dg/timeseries-forecasting-deploy-models.html) to build 
a time series predictor model for each satellite beam in the ship(s) path, accounting for the impact of weather
conditions in a given location. It then renders results in [Amazon QuickSight](https://aws.amazon.com/quicksight/) BI tooling, displaying
forecasted capacity needs, accuracy metrics, and which attributes most impact the model.

### Architecture
The architecture of the system is as follows: -

