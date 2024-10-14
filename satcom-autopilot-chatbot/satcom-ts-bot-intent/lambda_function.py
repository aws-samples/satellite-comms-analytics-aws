# Lambda function which interacts with Amazon Lex to provide users either
# a satellite capacity spot beam forecast provided by a Sagemaker timeseries model endpoint,
# or a response to generic satellite communications questions via a Bedrock-based LLM

import json
import boto3
import os
import botocore
from botocore.exceptions import ClientError
import logging
import uuid
from uuid import uuid4
import time
from datetime import datetime, timedelta
import argparse
import random

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# S3 folder location of Real Time inference sample input files to be passed to invoke_endpoint API
# change this if you use a different S3 folder structure
S3_FOLDER_PREFIX = 'dataset/rtinf/'


def lambda_handler(event, context):

    # this can be run either as cmd line py program or a Lambda based on the execution environment    
    execEnv = str(os.getenv('AWS_EXECUTION_ENV'))
    if execEnv.startswith("AWS_Lambda"):
        bucketName = os.getenv('bucketName')
        endpointName = os.getenv('endpointName')
        agent_id = os.getenv('agent_id')
        agent_alias_id = os.getenv('agent_alias_id')
    else:
        parser = argparse.ArgumentParser()
        parser.add_argument("-b", "--bucketname", help="This bucket has the input body for real time inference requests")
        parser.add_argument("-e", "--endpointName", help="satcom forecast endpoint created by Sagemaker Autopilot timeseries training")
        parser.add_argument("-a", "--agent_id", help="Bedrock agent id")
        parser.add_argument("-i", "--agent_alias_id", help="Bedrock alias agent id")
        args = parser.parse_args()
        bucketName = args.bucketname
        endpointName = args.endpointName
        agent_id = args.agent_id
        agent_alias_id = args.agent_alias_id

    if None in (bucketName, endpointName, agent_id, agent_alias_id):
        print("Invalid bucketName and/or endpointName and/or agent_id and/or agent_alias_id")
        return -1
    else:
        print("Bucket: ", bucketName, " Endpoint: ", endpointName, "Agent ID: ", agent_id, " Agent Alias ID: ", agent_alias_id)


    # bring in params from the bot ie intent and slot values
    logger.debug(event)
    
    intent = event['sessionState']['intent']
    
    session_attributes = {}
    session_attributes['sessionId'] = event['sessionId']
    
    intent_name = event['sessionState']['intent']['name']
    print("Intent name: ", intent_name)
    
    active_contexts = {}
    
    # Dispatch to your bot's intent handlers
    if intent_name == 'BeamForecast':
        
        slots = event['sessionState']['intent']['slots']
        spotBeam = try_ex(slots['SpotSlot'])
    
        # we use minimal, pre-canned Spot beam inputs to the Sagemaker endpoint
        # in a production use-case the S3 key would be a programmatic retrieval based on
        # date, time, spot-beam parameters
        # replace these csv's with your input csv's to your SageMaker endpoint
        if spotBeam == 'SpotH3':
            key = S3_FOLDER_PREFIX + 'satcom-autopilot-cap-SpotH3_1724274086.csv'
        elif spotBeam == 'SpotH7':
            key = S3_FOLDER_PREFIX + 'satcom-autopilot-cap-SpotH7_1724274106.csv'
        elif spotBeam == 'SpotH12':
            key = S3_FOLDER_PREFIX + 'satcom-autopilot-cap-SpotH12_1724274132.csv'
        elif spotBeam == 'SpotH15':
            key = S3_FOLDER_PREFIX + 'satcom-autopilot-cap-SpotH15_1724264904.csv'
        else:
            raise Exception('spotBeam ' + spotBeam + ' not supported')
            
        inf_data = get_object(bucketName, key)
        
        # now invoke the endpoint with our inference data body
        response = invoke_endpoint(endpointName, inf_data)
        prediction = response['Body'].read().decode()

        # print first few lines to sanity check prediction results
        pred_trim = prediction.splitlines()
        pred_snip = []
        for i in range(3):
            pred_snip.append(pred_trim[i])
            
        # convert back to string for Lex response
        pred_snip_str = '\n'.join(pred_snip)
        print(pred_snip_str)
            
        # now return the response to the bot intent
        intent['confirmationState']="Confirmed"
        intent['state']="Fulfilled"
        return close(session_attributes, active_contexts, intent, pred_snip_str)
    
    # if user asks a different question fulfil the answer via Bedrock agent and kbase
    elif intent_name == 'FallbackIntent':
        
        # get the user's question
        prompt = event['inputTranscript']
        # print(prompt)
        
        # now pass the prompt to our LLM to answer the question
        
        # Create a Bedrock Agent Runtime client in the AWS Region you want to use.
        client = boto3.client("bedrock-agent-runtime")
        
        session_id = str(uuid4())
        # prompt = "what is Carrier-to-noise ratio?"
        
        # Send the message to the agent 
        res = invoke_agent(client, agent_id, agent_alias_id, session_id, prompt)
        print(res)
        if (not res):
            res = "Could not get result answer from LLM"
        
        # now return the response to the bot intent
        intent['confirmationState']="Confirmed"
        intent['state']="Fulfilled"
        return close(session_attributes, active_contexts, intent, res)

    else:
        raise Exception('Intent with name ' + intent_name + ' not supported')

    return None



# helper functions...Lex chatbot

def try_ex(value):
    """
    Call passed in function in try block. If KeyError is encountered return None.
    This function is intended to be used to safely access dictionary of the Slots section in the payloads.
    Note that this function would have negative impact on performance.
    """

    if value is not None:
        return value['value']['interpretedValue']
    else:
        return None

# close ends the intent fulfillment process 
def close(session_attributes, active_contexts, intent, message):
    response = {
        'sessionState': {
            'activeContexts':[{
                'name': 'intentContext',
                'contextAttributes': active_contexts,
                'timeToLive': {
                    'timeToLiveInSeconds': 600,
                    'turnsToLive': 1
                }
            }],
            'sessionAttributes': session_attributes,
            'dialogAction': {
                'type': 'Close',
            },
            'intent': intent,
        },
        'messages': [{'contentType': 'PlainText', 'content': message}]
    }

    return response


# helper functions...Sagemaker endpoint
# function to invoke a Sagemaker endpoint
def invoke_endpoint(endpoint_name, payload):
    client = boto3.client('sagemaker-runtime')

    response = client.invoke_endpoint(
        EndpointName=endpoint_name,
        Body=payload,
        ContentType='text/csv')

    return response


# helper functions...Bedrock runtime agent
# invoke bedrock agent
def invoke_agent(client, agent_id, agent_alias_id, session_id, prompt):
    """
    Sends a prompt for the agent to process and respond to.

    :param agent_id: The unique identifier of the agent to use.
    :param agent_alias_id: The alias of the agent to use.
    :param session_id: The unique identifier of the session. Use the same value across requests
                       to continue the same conversation.
    :param prompt: The prompt that you want model to complete.
    :return: Inference response from the model.
    """

    try:
        # Note: The execution time depends on the foundation model, complexity of the agent,
        # and the length of the prompt
        response = client.invoke_agent(
            agentId=agent_id,
            agentAliasId=agent_alias_id,
            sessionId=session_id,
            inputText=prompt,
        )

        completion = ""

        for event in response.get("completion"):
            chunk = event["chunk"]
            # print(chunk)
            completion = completion + chunk["bytes"].decode()

    except ClientError as e:
        logger.error(f"Couldn't invoke agent. {e}")
        raise

    return completion


# helper functions...S3 objects
# function to get an object from S3 bucket
def get_object(bucket, key):
    s3 = boto3.resource('s3')
    try:
        obj = s3.Object(bucket, key).get()['Body'].read().decode('utf-8')
    except s3.meta.client.exceptions.ClientError as err:
        print('S3 bucket access issue: {}'.format(err.response['Error']['Message']))
        obj = None
    return obj




# allow local Python execution testing
if __name__ == '__main__':
    lambda_handler(None,None)
