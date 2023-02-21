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
  
For simplicity we bundle both of these modules into a single .zip layer as follows in a Linux terminal: -

```
[>] mkdir requests_opensearchpy_layer
[>] cd requests_opensearchpy_layer/
[>] mkdir python
[>] pip install --target ./python requests
[>] pip install --target ./python requests_aws4auth
[>] pip install --target ./python opensearch-py
[>] zip -r requests_opensearchpy_layer.zip python
[>] aws lambda publish-layer-version --layer-name requests_opensearchpy_layer --zip-file fileb://requests_opensearchpy_layer.zip --compatible-runtimes python3.8 python3.9 --region <YOUR-AWS-REGION>
[>] aws s3 cp requests_opensearchpy_layer.zip s3://<YOUR-S3-ASSETS-BUCKET>/kds-scripts/
```

Demystifying these steps we firstly create a layer directory, with (importantly!) a python subdirectory. Then we use the [Python package manager](https://pypi.org/project/pip/), pip, to install the requests, requests_aws4auth, and the opensearch-py modules. Next we zip it up and publish the Lambda layer specifying which Python runtime versions it has been tested with. Finally we copy the zipped layer to the S3 bucket so that we can reference it as an S3Key in our CloudFormation deployment template. 
  
Your S3 bucket folder should now look similar to the figure below: -

![Capture_osearch_S3_kds_blur](https://user-images.githubusercontent.com/122999933/220426956-1f11c945-b63d-4e77-8432-bd1d1afb00f6.png)

You are now ready to deploy the stack. Click Next, acknowledge the IAM resources creation, and click Submit. It will take 5-10 minutes to complete the deployment of all the AWS resources. 

The Kinesis Data Generator tool can also be used to input data to Kinesis Data Streams. Using the same satellite beam JSON record template as Pipeline 1, select the newly deployed Kinesis stream. Click “Send data” using any one of the 3 Beam record templates. Stop the data generation after approximately 1000 records. 
  
![Capture_KDG_osearch](https://user-images.githubusercontent.com/122999933/220427249-3eb5c9f1-2d61-4d4f-a7c5-0b3228b74d78.PNG)

Recall from Figure 10 that the stream triggers a Lambda function to postprocess the data into geo-mapping location coordinates for the OpenSearch dashboard. Let’s check the log files via Amazon CloudWatch to ensure the Lambda executed correctly. One way to navigate there is to look at the CloudFormation “Resources” tab. Click the Physical ID URL link of the Lambda Function. Next Click “Monitor” and “View CloudWatch Logs” – this takes you directly to the Log stream for the pipeline’s Lambda transformation. The Log streams should look similar to the figure below: -
  
![Capture_CW_osearch_blur](https://user-images.githubusercontent.com/122999933/220427425-9b7344f3-011b-4ad0-8ffd-610e3096bd07.png)

Next, navigate to OpenSearch via the AWS Console. There should be a Domain endpoint generated by the CloudFormation template. Clicking on this endpoint should display a JSON blob with the cluster name, version number etc.
  
*Troubleshooting tip*: If you get an error at this stage your IP may have changed versus what was entered in the CloudFormation parameters. 

Click on the “Indices” tab – you should see a Document count corresponding to the total number of records processed by the Lambda function.

Finally we are ready to construct our Satellite Communications Analytics OpenSearch dashboard. Click on the OpenSearch dashboards URL. The dashboard in Figure 11 can be created relatively quickly. For example to create the Number of Data points visual, click “Visualize” in the left hand menu -> Create visualization -> Metric -> select the index we created. It will then show the Count of samples. To create the Geo visualization select Coordinate map and configure the Metrics of interest against the Geo coordinates location field e.g. 


 
