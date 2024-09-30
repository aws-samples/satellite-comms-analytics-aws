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
via a [Lex channel integration](https://docs.aws.amazon.com/lexv2/latest/dg/deploying-messaging-platform.html).

This project provides the infrastructure, via a series of Cloudformation templates, for Lex, Lambda, Sagemaker endpoint, 
Bedrock knowledgebase and agent, and S3 assets. 

Depending on the user’s question the bot goes one of 2 different paths: -
* capacity forecast - if the user asks “get capacity” or similar utterances, we invoke the BeamForecast Lex intent, which in turn calls a Lambda function to invoke a Sagemaker Autopilot timeseries model endpoint. The model was trained on generated, synthetic satellite data - the Notebook is available at https://github.com/aws-samples/satellite-comms-forecast-aws/tree/main/autopilot-notebook 
* satellite communication topics - if the user asks a question related to the field of satellite communication, but not directly requesting a specific forecast, the FallbackIntent is invoked. The same Lambda handles this path, but instead invokes a Claude3 Bedrock agent associated with a Bedrock knowledge-base consisting of AWS Satellite Communication blogs. 

As illustrated in the architecture diagram, we use the following AWS services:

- [SageMaker](https://aws.amazon.com/sagemaker/) to invoke the Satellite Capacity Autopilot inference endpoint for spot beam predictions
- [Bedrock](https://aws.amazon.com/bedrock/) for access to the FMs for
  embedding and text generation as well as for the knowledge base agent.
- [Lambda](https://aws.amazon.com/lambda/) to call either the Sagemaker endpoint with the BeamForecast Lex intent or the Bedrock LLM KB agent via the Fallback intent.
- [OpenSearch Service Serverless with vector
  search](https://aws.amazon.com/opensearch-service/serverless-vector-engine/)
  for storing the embeddings of the enterprise knowledge corpus and
  doing similarity search with user questions.
- [S3](https://aws.amazon.com/pm/serv-s3/) for storing the raw knowledge
  corpus data (PDF, HTML files).
- [AWS Identity and Access Management](https://aws.amazon.com/iam/)
  roles and policies for access management.
- [AWS CloudFormation](https://aws.amazon.com/cloudformation/) for
  creating the entire solution stack through infrastructure as code.


# Deployment Guide 

In the following sections, we discuss the key steps to deploy the solution, including pre-deployment and post-deployment.

# Pre-Deployment
An AWS account to deploy the resources. Please use the link to sign-up if you do not have an account [AWS
account](https://signin.aws.amazon.com/signin?redirect_uri=https%3A%2F%2Fportal.aws.amazon.com%2Fbilling%2Fsignup%2Fresume&client_id=signup)

**Note** - navigate to Amazon Bedrock Console and ensure that you have access to the models you are going to use in this solution e.g. Claude 3.5 Sonnet

Clone the repository using the command 
`git clone https://github.com/aws-samples/satellite-comms-forecast-aws.git`

The SageMaker endpoint needs to be available for this project to use. Follow the steps 
[here](https://github.com/aws-samples/satellite-comms-forecast-aws/tree/main/autopilot-notebook) to 
create a SageMaker Autopilot time-series real-time inference endpoint. At the end you should have a model as follows: -

![Capture-Sage-endpoint-bluracctid](https://github.com/user-attachments/assets/86e68bda-f557-45c4-9ce3-f2f3c349e111)


# Deployment Steps
**Note** - this project shares many of the same deployment steps as [this project](https://github.com/aws-samples/amazon-bedrock-rag-knowledgebases-agents-cloudformation) hence
feel free to use it as an additional reference.

The solution deployment automation script uses 3 parameterized CloudFormation template, OpenSearch_serverless.yaml, satcom-ts-kb-agent.yaml, and satcom-ts-lexbot.yaml to automate provisioning of following solution resources:
 
 1. OpenSearch Service Serverless collection
 2. Amazon Bedrock KnowledgeBase
 3. Amazon Bedrock Agent
 4. AWS Lambda 
 5. Amazon Lex chatbot intents
 6. IAM Roles


# Cloudformation to deploy OpenSearch_serverless.yaml stack
AWS CloudFormation prepopulates stack parameters with the default values provided in the template except for ARN of the IAM role with which you are
currently logged into your AWS account which you’d have to provide. To provide alternative input values, you can specify parameters as environment variables that are referenced in the `ParameterKey=<ParameterKey>,ParameterValue=<Value>` pairs in the following shell script’s `aws cloudformation create-stack --stack-name <stack-name> --template-body file://OpenSearch_serverless.yml --capabilities CAPABILITY_NAMED_IAM --parameters ParameterKey=<parameter key>,ParameterValue=<parameter value>` ....

**Note** - make sure you have sufficient IAM permissions in the IAM role you pass in to use Amazon OpenSearch

**Note** - currently the stack can only be deployed in us-east-1 and us-west-2

Once the Cloudformation stack creation is successful navigate to the Output section of the stack and grab the following output values `AmazonBedrockExecutionRoleForKnowledgeBasearn`, `AOSSIndexName`. We will use these values as parameters for our next stack satcom-ts-kb-agent.yaml to deploy Amazon Bedrock Knowledgebase and agents.

## Create Vector index in OpenSearch Serverless
The previous CloudFormation stack creates an OpenSearch Service Serverless collection, but the next step will require us to create a vector index in the collection. Follow the steps outlined below: 

1.  Navigate to OpenSearch Service console and click on `Collections`.
    The `satcom-aoss-coll` collection created by the CloudFormation stack
    will be listed there.

2.  Click on the `satcom-aoss-coll` link to create a vector index for
    storing the embeddings from the documents in S3. Next, click `Create vector index`

3. Grab the vector index name from the output values of the previous stack, the default value is`satcom-aoss-index`. Input the vector
    field name as `vector` dimensions as `1024`, choose engine types as `FAISS` and distance metric as
    `Euclidean`. **It is required that you set these parameters exactly
    as mentioned here because the Bedrock Knowledge Base Agent is going
    to use these same values**.
  
4.  Once created the vector index is listed as part of the collection.

![Capture-aoss-vector](https://github.com/user-attachments/assets/d3046262-98b6-4afd-95af-67824694abb3)


  
