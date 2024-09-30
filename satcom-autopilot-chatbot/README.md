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

![satcapacitybot-arch drawio](https://github.com/user-attachments/assets/273e9557-edf1-4414-8bc3-fe864691d077)

Users interact with the application via either Amazon Lex directly or a Messaging platform such as Facebook, Slack or Twilio. This is achieved
via a [Lex channel integration][https://docs.aws.amazon.com/lexv2/latest/dg/deploying-messaging-platform.html].

This project provides the infrastructure, via a series of Cloudformation templates, for Lex, Lambda, Sagemaker endpoint, 
Bedrock knowledgebase and agent, and S3 assets. 

Depending on the user’s question the bot goes one of 2 different paths: -
* capacity forecast - if the user asks “get capacity” or similar utterances, we invoke the BeamForecast Lex intent, which in turn calls a Lambda function to invoke a Sagemaker Autopilot timeseries model endpoint. The model was trained on generated, synthetic satellite data - the Notebook is available at https://github.com/aws-samples/satellite-comms-forecast-aws/tree/main/autopilot-notebook 
* satellite communication topics - if the user asks a question related to the field of satellite communication, but not directly requesting a specific forecast, the FallbackIntent is invoked. The same Lambda handles this path, but instead invokes a Claude3 Bedrock agent associated with a Bedrock knowledge-base consisting of AWS Satellite Communication blogs. 

