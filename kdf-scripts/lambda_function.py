# Lambda function to tweak the KDF records to make them more Satellite/NMS-like

import base64
import os
import json

print('Loading function ')


def lambda_handler(event, context):
    output = []

    i = 0
    latInc = 0
    longInc = 0
    
    # print("Event: ", event)
    
    for record in event['records']:
#        print(record['recordId'])
        payload = base64.b64decode(record['data']).decode('utf-8')

        # Do custom processing on the payload here
        pJson = json.loads(payload)

        latInc += 0.01
        pJson["latitude"] += latInc
        
        longInc -= 0.001
        pJson["longitude"] += longInc
        
        pJson["fwdBitRate"] = pJson["fwdBitRate"] + (pJson["fwdModCodId"] * 0.75)
        
        # fake a bad packetLoss scenario
        if pJson["latitude"] > 42.0 and pJson["latitude"] < 43.0:
            pJson["packetsLost"] *= 1000

        # fake lost Rx lock
        if pJson["latitude"] > 63.0 and pJson["latitude"] < 64.0:
            pJson["fwdSNR"] = -100.0

        
        if i % 100 == 0:
#           print(pJson)
           print ("Lat: ", pJson["latitude"], "Lon: ", pJson["longitude"], "fwdBitRate: ", pJson["fwdBitRate"], "Pkts lost: ", pJson["packetsLost"])
        i += 1
        
        output_record = {
            'recordId': record['recordId'],
            'result': 'Ok',
            'data': base64.b64encode(json.dumps(pJson).encode('utf-8'))
        }
        output.append(output_record)

    print('Successfully processed {} records.'.format(len(event['records'])))

    return {'records': output}
