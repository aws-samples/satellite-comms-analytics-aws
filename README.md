## Satellite Communications Analytics on AWS

### Description
This repoistory contains pipelines to demonstrate Satellite Communications Analytics use-cases.
It is intended to leverage AWS Serverless Analytics to show how to get Insights on key KPIs
e.g. SNR, Modulataion & Coding Rates. Additionally Machine Learning (Sagemaker) is 
used to detect anomalies.

### AWS Technologies used

One of the key goals of this SatCom assets repository is to leverage AWS Serverless Analytics

* Kinesis Data Streams 
* Kinesis Firehose
* Lambda
* Glue
* Athena
* QuickSight
* Opensearch
* Sagemaker Studio
* Sagemaker Serverless Inference
* Amazon S3
* Amazon CloudWatch
* Cloudformation templates

## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This library is licensed under the MIT-0 License. See the LICENSE file.

## Analytics Pipelines

This github repository and associated Blog contains artifacts for 3 pipelines: -
* Streaming to a data lake, ETL transformation, Business Intelligence
* Real-Time Monitoring in Amazon OpenSearch
* Train a model with SageMaker and deploy a Serverless Inference

The first pipeline is fully described in the Blog post, to allow readers to walk through
the process via the article itself. The HowTo for the 2nd and 3rd pipelines are described here 
to keep the Blog post smaller. 

### Pipeline 2 – Real-Time Monitoring in Amazon OpenSearch

![idx-kinesis-opensearch](https://user-images.githubusercontent.com/122999933/220422882-4d2cbd49-3458-44e2-b817-aa1ad5ae8609.png)

This figure represents a Reference Architecture for Real-Time streaming of metrics to [Amazon OpenSearch](https://aws.amazon.com/opensearch-service/), an open source, distributed search and analytics suite derived from Elasticsearch. Widgets such as heat-maps and geo-mapping can be added via the popular Kibana user interface to rapidly create rich Business Analytics dashboards

To deploy this solution in your own AWS account, click “Create stack (with new resources)” in the AWS CloudFormation console. Next, download  [streaming_kinesis_lambda_osearch.yaml](./streaming_kinesis_lambda_osearch.yaml) template, select “Upload a template file” & browse to the yaml file. 
The parameters for this CloudFormation template are as shown in the table below: -

| Parameter      | Default     | Description |
| -------------- | ----------- | ----------- |
| LambdaZipName  | kds-scripts/satcom-wshop-rt-geo-lambda.zip | Name of the Kinesis Data Streams Lambda zip file |
| OpenSearchAllowedIPs |         | Comma-delimited list of IP addresses accessing OpenSearch domain |
| SatComAssetsS3Bucket |         | Holds helper assets eg Glue python transforms |

The Lambda function is referenced in the same fashion as Pipeline 1, via a Zip file in an S3 bucket. Simply zip up the python function [here](./kds-scripts/lambda_function.py) and add it to the S3 bucket similar to the kds-scripts/<name-of-file>.zip parameter supplied above.

The OpenSearchAllowedIPs parameter can simply be your public IPv4 IP as detected by https://www.whatismyip.com/. Bear in mind this IP can change based on your Internet Service Provider (ISP) hence you can enter several IPs or CIDR ranges via a comma-delimited list. 

The SatComAssetsS3Bucket can/should be the same as the assets bucket used in Pipeline 1. 
  
There is one additional factor to be considered. The Lambda runtime cannot contain all possible libraries and dependencies a given function may need. In order to submit indices to OpenSearch via the AWS Python SDK we need the requests_aws4auth and the opensearchpy modules. [Lambda layers](https://docs.aws.amazon.com/lambda/latest/dg/configuration-layers.html) provide a convenient way to package these libraries via a .zip file archive. 
  


  
