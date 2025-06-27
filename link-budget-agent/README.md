# Link Budget Calculator Agent

This project provides an Amazon Bedrock Agent that calculates satellite link budgets using a containerized AWS Lambda function. The agent uses natural language processing to collect parameters from users and invoke the link budget calculation through an action group.

## Architecture Overview

The solution consists of:
- **AWS Lambda Function**: Containerized function using the [link-budget](https://github.com/igorauad/link-budget) Python package
- **Amazon Bedrock Agent**: AI agent with Claude 3.5 Sonnet v2 that handles user interactions
- **Action Group**: Connects the agent to the Lambda function with defined parameters
- **CloudFormation Templates**: Infrastructure as Code for automated deployment

## Lambda Function

### Overview
The Lambda function is built as a container image and uses the open-source [link-budget Python package](https://github.com/igorauad/link-budget) to perform satellite communication link budget calculations with sensible default parameters.

### Building the Lambda Function

> [!NOTE]
> The link budget python package has dependencies which may not be satisfied with
> the most recent Python versions. This Lambda function was tested with Python 3.10
> in a [virtual environment](https://www.freecodecamp.org/news/how-to-setup-virtual-environments-in-python/)

1. **Prerequisites**:
   - Docker installed and running
   - AWS CLI configured
   - ECR repository access


2. **Build and Deploy**:

   A docker container image is used for the lambda function instead of a [.zip file archive](https://docs.aws.amazon.com/lambda/latest/dg/python-package.html) because the size of the dependencies for the link-budget package exceeds 250Mb.

   ```bash
   # Make the script executable
   chmod +x build-and-deploy.sh
   
   # Build and deploy the container
   ./build-and-deploy.sh link-budget-lambda us-east-1 123456789012
   ```
   Replace parameters as appropriate (i) lambda function name (ii) AWS region, (iii) your AWS account id.


3. **Deploy Lambda with CloudFormation**:
   ```bash
   aws cloudformation create-stack \
     --stack-name link-budget-lambda-stack \
     --template-body file://link-budget-lambda-cfn.yaml \
     --parameters ParameterKey=ImageUri,ParameterValue=123456789012.dkr.ecr.us-east-1.amazonaws.com/link-budget-lambda:latest \
     --capabilities CAPABILITY_NAMED_IAM \
     --region us-east-1
   ```

### Lambda Function Features
- **Container-based deployment** for better dependency management
- **AMD64 platform compatibility** with AWS Lambda
- **Bedrock action group** integration support
- **Comprehensive parameter handling** with sensible defaults
- **CloudWatch logging** with configurable log levels

## Amazon Bedrock Agent

### Overview
The Bedrock Agent provides a conversational interface for satellite link budget calculations. It uses Claude 3.5 Sonnet v2 (configurable) to understand user requests and collect the necessary parameters.

### Agent Capabilities
- **Natural Language Processing**: Understands user requests in plain English
- **Parameter Collection**: Intelligently asks for required parameters
- **Calculation Invocation**: Calls the Lambda function through action groups
- **Result Interpretation**: Presents calculation results in a user-friendly format

### Action Group Configuration
The agent includes one action group:

**LinkBudgetCalculator Action Group**:
- **Function**: `calculateLinkBudget`
- **Required Parameters**:
  - `coax_length` (number): Coaxial cable length in feet
  - `rx_dish_gain` (number): Receive dish gain in dBi
- **Optional Parameters**: All other link budget parameters for enhanced accuracy

### Supported Parameters
| Parameter        | Type | Required | Description                  | Default |
|------------------|------|----------|------------------------------|---------|
| coax_length      | number | ✓ | Coaxial cable length in feet | -       |
| rx_dish_gain     | number | ✓ | Receive dish gain in dBi     | -       |
| atmospheric_loss | number | | Atmospheric loss in dB       | 0.5     |
| rx_noise_fig     | number | | rx_noise_fig                 | 8.0     |
| eirp             | number | | antenna EIRP in dBW          | 50      |

> [!TIP]
> You can increase the number of parameters by submitting a quota increase
> request [here](https://us-east-1.console.aws.amazon.com/servicequotas/home/services/bedrock/quotas)

## Deployment

### Deploy the Bedrock Agent

1. **Prerequisites**:
   - Lambda function deployed and ARN available
   - Appropriate IAM permissions for Bedrock
   - Ensure you have access to the FM model of choice

2. **Deploy with CloudFormation**:
   ```bash
   aws cloudformation create-stack \
     --stack-name link-budget-bedrock-agent-stack \
     --template-body file://bedrock-agent-template.yaml \
     --parameters ParameterKey=LambdaFunctionArn,ParameterValue=arn:aws:lambda:region:account:function:link-budget-calculator \
     --capabilities CAPABILITY_NAMED_IAM \
     --region us-east-1
   ```

3. **Customization Options**:
   ```bash
   # Use different model
   --parameters ParameterKey=ModelId,ParameterValue=anthropic.claude-3-haiku-20240307-v1:0
   
   # Custom agent name
   --parameters ParameterKey=AgentName,ParameterValue=MyLinkBudgetAgent
   ```

### Template Parameters
- **AgentName**: Name for the Bedrock Agent (default: LinkBudgetAgent)
- **ModelId**: Foundation model ID (default: Claude 3.5 Sonnet v2)
- **LambdaFunctionArn**: ARN of the Lambda function
- **AgentInstruction**: Custom instructions for the agent behavior

## Usage Examples

### Interacting with the Agent

1. **Basic Calculation**:
   ```
   User: "Calculate a link budget for a 100-foot coax cable and 35 dBi dish gain"
   Agent: [Collects parameters and performs calculation]
   ```

2. **Advanced Calculation**:
   ```
   User: "get link margin"
   Agent: [Asks for required parameters - dish gain and coax length]
   ```

   ```
   User: "I need a link budget for Ku-band at 12.5 GHz with a 1.2m dish"
   Agent: [Asks for required parameters and uses provided frequency and dish size]
   ```

3. **Parameter Clarification**:
   ```
   User: "What's the link margin for my setup?"
   Agent: "I'll help you calculate that. I need the coaxial cable length and receive dish gain..."
   ```

## File Structure

```
link-budget/
├── lambda_function.py              # Lambda function code
├── requirements.txt                # Python dependencies
├── Dockerfile                      # Container image definition
├── link-budget-lambda-cfn.yaml     # Lambda deployment template
├── bedrock-agent-template.yaml     # Bedrock agent template
├── build-and-deploy.sh             # Build and deployment script
└── README.md                       # This file
```

## References and Documentation

### AWS Documentation
- [AWS Lambda Container Images](https://docs.aws.amazon.com/lambda/latest/dg/images-create.html)
- [Amazon Bedrock Agents](https://docs.aws.amazon.com/bedrock/latest/userguide/agents.html)
- [Bedrock Action Groups](https://docs.aws.amazon.com/bedrock/latest/userguide/agents-action-create.html)
- [CloudFormation Lambda Reference](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-lambda-function.html)
- [CloudFormation Bedrock Agent Reference](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-bedrock-agent.html)

### GitHub Repositories
- [Link Budget Python Package](https://github.com/igorauad/link-budget) - Core calculation library
- [AWS Lambda Container Images Examples](https://github.com/aws-samples/aws-lambda-container-image-converter)
- [Amazon Bedrock Samples](https://github.com/aws-samples/amazon-bedrock-samples)

## Troubleshooting

### Common Issues

1. **Container Build Failures**:
   - Ensure Docker is running
   - Check platform compatibility (use `--platform linux/amd64`)
   - Verify all dependencies in requirements.txt
   - Use a version of python that is compatible with the link budget python package (e.g. 3.10) 

2. **Lambda Deployment Issues**:
   - Confirm ECR repository exists
   - Check IAM permissions for ECR and Lambda
   - Verify image URI format

3. **Bedrock Agent Issues**:
   - Ensure Lambda function ARN is correct
   - Check IAM role permissions
   - Verify model availability in your region

4. **Action Group Invocation Failures**:
   - Check Lambda resource-based policy for Bedrock
   - Verify function schema matches Lambda handler
   - Review CloudWatch logs for errors

### Monitoring and Logging

- **Lambda Logs**: Available in CloudWatch under `/aws/lambda/link-budget-calculator`
- **Bedrock Agent Logs**: Check CloudWatch for agent execution logs
- **Build Logs**: Monitor Docker build output and ECR push status

## Cost Considerations

- **Lambda**: Pay per invocation and execution time
- **Bedrock**: Pay per input/output tokens and model usage
- **ECR**: Storage costs for container images
- **CloudWatch**: Log storage and retention costs

For detailed pricing, visit the [AWS Pricing Calculator](https://calculator.aws).

## Security Best Practices

- Use least-privilege IAM policies
- Enable CloudTrail for API logging
- Regularly update container base images
- Monitor usage patterns and set up alerts
- Use VPC endpoints for private communication (if required)

## Contributing

To contribute to this project:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project uses the [link-budget](https://github.com/igorauad/link-budget) package. Please refer to the original repository for licensing information.
