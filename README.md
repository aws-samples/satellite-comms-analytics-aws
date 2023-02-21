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

To deploy this solution in your own AWS account, click “Create stack (with new resources)” in the CloudFormation console. Next, download the streaming_kinesis_lambda_osearch.yaml  template from the GitHub repository, select “Upload a template file” & browse to the yaml file. 
The parameters for this CloudFormation template are as shown in Figure 12: -
