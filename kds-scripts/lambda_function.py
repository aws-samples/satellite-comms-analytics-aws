import base64
import boto3
import json
import os
import string
import requests
from requests_aws4auth import AWS4Auth

from opensearchpy import OpenSearch, RequestsHttpConnection

region = os.environ['AWS_REGION']
service = 'es'
credentials = boto3.Session().get_credentials()
awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)

# the OpenSearch Service domain (minus the https://)
# host = f"search-name-a1bcdefgh23456.{region}.es.amazonaws.com" 
port = 443
index = 'lambda-geo-index4'


def lambda_handler(event, context):
    
    count = 0
    i = 0
    latInc = 0
    longInc = 0
    
    # get the OpenSearch domain endpoint from environment variable, and strip the https://
    # endpoint appears to have changed ie no longer has https:// prefix so handle both cases
    endpoint = os.environ['endpoint']
    hostnm = endpoint.partition("https://")
    print("Region: ", region)
    print("endpoint: ", endpoint)
    if not hostnm[2]:
        hostname = endpoint
    else:
        hostname = hostnm[2]
    print("hostname: ", hostname)
    
    client = OpenSearch(
        hosts = [{'host': hostname, 'port': port}],
        http_auth = awsauth,
        use_ssl = True,
        verify_certs = True,
        ssl_assert_hostname = False,
        ssl_show_warn = False,
        connection_class=RequestsHttpConnection
    )
    # print("Client info: ", client.info())
    
    body = {
        "mappings": {
            "properties": {
                "location": {
                    "type": "geo_point"
                }
            }
        }
    }
    try:
        response = client.indices.create(index, body=body)
        print("Client index create response: ", response)
    except:
        print("Already created index: ", index)
    
    
    for record in event['Records']:
        id = record['eventID']
        timestamp = record['kinesis']['approximateArrivalTimestamp']

        # Kinesis data is base64-encoded, so decode here
        message = base64.b64decode(record['kinesis']['data'])

        # Create the JSON document
        # Do custom processing on the payload here
        pJson = json.loads(message)

        latInc += 0.05
        pJson["latitude"] += latInc
        
        longInc -= 0.005
        pJson["longitude"] += longInc
        
        pJson["fwdBitRate"] = pJson["fwdBitRate"] + (pJson["fwdModCodId"] * 0.75)
        
        # fake a bad packetLoss scenario
        if pJson["latitude"] > 42.0 and pJson["latitude"] < 43.0:
            pJson["packetsLost"] *= 1000

        # fake lost Rx lock
        if pJson["latitude"] > 63.0 and pJson["latitude"] < 64.0:
            pJson["fwdSNR"] = -100.0

        pJson["location"] = {}
        pJson["location"]["lat"] = pJson["latitude"]
        pJson["location"]["lon"] = pJson["longitude"]

        # Index the document
        # r = requests.put(url + id, auth=awsauth, data=json.dumps(pJson), headers=headers)
        
        client.index(index=index, id=id, body=json.dumps(pJson))

        if i % 10 == 0:
           print ("Lat: ", pJson["latitude"], "Lon: ", pJson["longitude"], "fwdBitRate: ", pJson["fwdBitRate"], "Pkts lost: ", pJson["packetsLost"])
#           print("r status_code: ", r.status_code, "r text: ", r.text)
        i += 1
        
        count += 1
    
    print("Processed: ", str(count), " items.")
    
    client.indices.refresh(index=index)
    res = client.cat.count(index=index, format="json")
    print(res)
    
    return
