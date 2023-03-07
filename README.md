## Satellite Communications Analytics on AWS

### Description
This repoistory contains pipelines to demonstrate Satellite Communications Analytics use-cases.
It is intended to leverage AWS Serverless Analytics to show how to get Insights on key KPIs
e.g. SNR, Modulataion & Coding Rates. Additionally Machine Learning (Sagemaker) is 
used to detect anomalies.

### AWS Technologies used

One of the key goals of this SatCom assets repository is to leverage AWS Serverless Analytics

* Amazon Kinesis Data Streams 
* Amazon Kinesis Data Firehose
* AWS Lambda
* AWS Glue
* Amazon Athena
* Amazon QuickSight
* Amazon Opensearch Service
* Amazon Sagemaker
* Amazon S3
* Amazon CloudWatch
* AWS CloudFormation

## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This library is licensed under the MIT-0 License. See the LICENSE file.

## Analytics Pipelines

This github repository and associated Blog contains artifacts for 3 pipelines: -
* Streaming to a data lake, ETL transformation, Business Intelligence
* Real-Time Monitoring and geo-mapping in Amazon OpenSearch
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

![Capture_Geo_osearch_viz](https://user-images.githubusercontent.com/122999933/220427755-81260119-1c51-490f-9f8c-26690fffffb6.PNG)

### Pipeline 3 – Detect Anomalies using Amazon SageMaker Random Cut Forest
Pipeline 3 demonstrates using the SageMaker [Random Cut Forest Algorithm](https://docs.aws.amazon.com/sagemaker/latest/dg/randomcutforest.html) to detect anomalous SNR values within our dataset. The algorithm is deployed to a [SageMaker Serverless Inference](https://docs.aws.amazon.com/sagemaker/latest/dg/serverless-endpoints.html) Endpoint. The detected SNR value anomalies are written to S3 for archival. The following figure represents the architecture used in this pipeline

![pipeline_3_architecture](https://user-images.githubusercontent.com/123971998/223513301-3985202d-9265-458a-bbc6-77e868104b56.png)


The environment which will be used to run the Jupyter [Notebook](https://github.com/aws-samples/satellite-comms-analytics-aws/blob/main/sagemaker-notebook/random_cut_forest_workshop.ipynb) file is SageMaker Studio. [SageMaker Studio](https://aws.amazon.com/sagemaker/studio/) is a web-based Integrated Development Environment (IDE) to prepare data, build, train, deploy, and monitor your machine learning models. The first time opening SageMaker Studio will require users to create a Domain and an Execution role. Once SageMaker Studio is configured and open, we import the Notebook file and specify an instance type of ml.t3.medium as seen in the following Figure.
  
![pipeline_3_notebook_selection](https://user-images.githubusercontent.com/123971998/223513109-f929c02a-3748-420b-99bc-221c630d29c5.png)

  
Within the Notebook file, the first thing which needs to be validated is [SageMaker Execution Role](https://docs.aws.amazon.com/sagemaker/latest/dg/sagemaker-roles.html) permissions. The role needs to be able to read from the S3 Output Bucket from the previous section. Additionally, write permissions are required for the SageMaker Session default bucket.

Next, we will reference the S3 Output Bucket for import. The Glue transformed data is represented as timeseries data configured in JSON lines files. Depending on how much data was generated using the Kinesis Data Generator, there may be multiple part files. We need to specify BUCKET_NAME and BUCKET_PREFIX displayed in the following code block. It’s important to note the prefix path will point to the location of the files so that multiple files at that location can be imported.
  ```
  # *** Edit the following bucket name and prefix to read the json lines part files *** 
downloaded_data_bucket = "BUCKET_NAME"
# To read multiple part files, specify the prefix leading to the files, ex. "year=2022/month=12/day=21/hour=16/"
downloaded_data_prefix = "BUCKET_PREFIX"
```
After importing the data, we plot the SNR value timeseries data which is displayed in the following Figure. We expect anomalies to be when the SNR value drops to -100. To further prepare the data, we convert to a [Pandas Dataframe](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.html). This conversion simplifies the input to the SageMaker Random Cut Forest Algorithm. The parameters have been set for the given example; however, they will need to be configured to reflect the data when applied to other datasets. As seen in the following code block, we call the fit function while passing in the dataset. This initiates a [SageMaker Training Job](https://docs.aws.amazon.com/sagemaker/latest/dg/how-it-works-training.html).
  
![pipeline_3_value_plot](https://user-images.githubusercontent.com/123971998/223512572-a29d44a3-b31d-43d3-afc4-93f5b74c653a.png)

```
# automatically upload the training data to S3 and run the training job
rcf.fit(rcf.record_set(satcom_data.value.to_numpy().reshape(-1, 1)))  
```
  
After the Training Job is complete, we deploy the model to a Serverless Inference Endpoint. Serverless Inference allows you to easily deploy Machine Learning models without configuring or managing any of the underlying infrastructure. SageMaker will automatically provision, scale, and turn off compute capacity based on the volume of inference request. This means you pay only for the duration of running the inference code and amount of data processed, not for idle periods. For this example, we have allocated 2048MB and specified a max concurrency of 5. See the following resource for more information about [configuring Serverless Inference](https://docs.aws.amazon.com/sagemaker/latest/dg/serverless-endpoints.html#serverless-endpoints-how-it-works-memory). 

Next, we use the trained model to identify anomalies in the dataset. Shown in the following code block, we call the predict function which generates an anomaly score for the SNR values. We overlay the anomaly scores against the SNR values which shows a jump in anomaly score value when the SNR value drops to -100. This is visualized in the following Figure. We can set a threshold based on Standard Deviation and add to our plot to visualize exactly where anomalies are.
```
results = rcf_inference.predict(satcom_data_numpy)  
```  
![pipeline_3_value_anomaly_plot](https://user-images.githubusercontent.com/123971998/223512132-4087cb5d-1bf1-430e-bd24-26ce00c71393.png)
  
Lastly, we write the anomalies to S3 as JSON lines format as seen in the following Figure. For an additional exercise, [S3 Event Notifications](https://docs.aws.amazon.com/AmazonS3/latest/userguide/NotificationHowTo.html) can be configured so that downstream applications or alerts can be triggered to execute when the anomalies are written to S3. Additional future exercises might include building on the SageMaker Serverless Inference Endpoint by [integrating with API Gateway and Lambda](https://aws.amazon.com/blogs/machine-learning/call-an-amazon-sagemaker-model-endpoint-using-amazon-api-gateway-and-aws-lambda/). The last step in the Notebook involves cleaning up the SageMaker Serverless Inference Endpoint.
 
![pipeline_3_anomalies](https://user-images.githubusercontent.com/123971998/223512838-88b65695-4a8c-49a0-a22f-1cccecfe25b2.png)

