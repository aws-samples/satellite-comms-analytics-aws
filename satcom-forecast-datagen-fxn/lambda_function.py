# Generate TTS and RTS for Forecast of SatCom Mhz usage by spot-beam

import json
import boto3
import os
import botocore
from botocore.exceptions import ClientError
import logging
import uuid
import time
from datetime import datetime, timedelta
import argparse
import random


startyear = 2023
startmonth = 4
startday = 1

spotBeams = ['SpotH3', 'SpotH7', 'SpotH12', 'SpotH15']

numRecs = 144 * 28       # TTS data : 28d
horizonRecs = 144        # RTS forecast : 1d (10 min granularity : 6 * 24)


def lambda_handler(event, context):

    # this can be run either as cmd line py program or a Lambda based on the execution environment    
    execEnv = str(os.getenv('AWS_EXECUTION_ENV'))
    if execEnv.startswith("AWS_Lambda"):
        bucketName = os.getenv('bucketName')
        ttsSatComUsage = os.getenv('ttsSatComUsage')
        rtsWeather = os.getenv('rtsWeather')
    else:
        parser = argparse.ArgumentParser()
        parser.add_argument("-b", "--bucketname", help="This bucket will hold the Forecast input data")
        parser.add_argument("-t", "--ttsSatComUsage", help="This file will be generated with SatCom usage")
        parser.add_argument("-r", "--rtsWeather", help="This file will be generated with Weather data")
        args = parser.parse_args()
        bucketName = args.bucketname
        ttsSatComUsage = args.ttsSatComUsage
        rtsWeather = args.rtsWeather

    if None in (bucketName, ttsSatComUsage, rtsWeather):
        print("Invalid bucketName and/or output files")
        return -1
    else:
        print("Bucket: ", bucketName, " TTS file: ", ttsSatComUsage, " RTS file: ", rtsWeather)

    # set the initial date/time for the TTS dataset
    initDate = datetime(startyear, startmonth, startday)
    print (initDate)

    tts_records = []
    rts_records = []
    i = 0
    ts = initDate
    surgeMultiplier = 1.0
    weatherMultiplier = 1.0
    for i in range(numRecs + horizonRecs):
        
        # add surge capacity usage to show peak usage time eg 01:00 -> 02:00
        dt = ts.time()
        hr = dt.hour
        if hr in range(1,3):
            surgeMultiplier = 1.5
        else:
            surgeMultiplier = 1.0
        
        # apply bad weather from to show datarate impact from time eg 06:00 -> 09:00
        if hr in range(6,9):
            weatherMultiplier = 0.8
        else:
            weatherMultiplier = 1.0
        
        # dummy variable encodings - helps forecast with day of week and hour observations
        day_of_week = ts.weekday()
        
        
        for b in spotBeams:
        
            if i < numRecs:
                tts_rec = {}
                tts_rec['timestamp'] = ts
                tts_rec['beam'] = b
                
                if tts_rec['beam'] == 'SpotH7':
                    tts_rec['mHz'] = random.randint(250,300)
                else:
                    tts_rec['mHz'] = random.randint(200,250)
                tts_rec['mHz'] = tts_rec['mHz'] * surgeMultiplier
            
            
            rts_rec = {}
            rts_rec['timestamp'] = ts
            rts_rec['beam'] = b
            rts_rec['dayofweek'] = day_of_week
            rts_rec['hourofday'] = hr
            
            if rts_rec['beam'] == 'SpotH12' and hr in range(6,9):
                rts_rec['airpressure'] = random.randint(950,1000)
                if i < numRecs:
                    tts_rec['mHz'] = tts_rec['mHz'] * weatherMultiplier
            else:
                rts_rec['airpressure'] = random.randint(1000,1050)
            
            
            if i < numRecs:
                tts_records.append(tts_rec)
            rts_records.append(rts_rec)
        
        # increment date by 10 mins for next mHz datapoint
        ts = ts + timedelta(minutes=10)
            
    
    tts_recs = fmt_tts_recs(tts_records)
    rts_recs = fmt_rts_recs(rts_records)
    
    # put TTS and RTS in separate folders for simpler BI tools (eg QuickSight) ingest
    put_object(bucketName, "dataset/tts/", tts_recs, ttsSatComUsage)
    put_object(bucketName, "dataset/rts/", rts_recs, rtsWeather)
    
    return None


# helper functions...

# format TTS record entries
def fmt_tts_recs(recs):
    
    tts_str = ""
    for i in range(len(recs)):
        tts_str = tts_str + str(recs[i]['timestamp']) + "," + str(recs[i]['mHz']) + "," + recs[i]['beam'] + "\n"
        
    return tts_str
    

# format RTS record entries
def fmt_rts_recs(recs):
    
    rts_str = ""
    for i in range(len(recs)):
        rts_str = rts_str + str(recs[i]['timestamp']) + "," + str(recs[i]['airpressure']) + "," + \
        recs[i]['beam'] + "," + str(recs[i]['dayofweek']) + "," + str(recs[i]['hourofday']) + "\n"
        
    return rts_str

    
# function to put an object into S3 bucket
def put_object(bucket, key, data, filename):
    
    dt_1 = datetime.now()
    dt_secs = int(dt_1.timestamp())

    f_name = os.path.splitext(filename)[0]
    f_name = f_name + "_" + str(dt_secs) + ".csv"
    
    key = key + f_name
    
    s3 = boto3.resource('s3')
    try:
        s3.Object(bucket, key).put(Body=data)
    except s3.meta.client.exceptions.ClientError as err:
        print('S3 bucket access issue: {}'.format(err.response['Error']['Message']))
        
    return True
    


# allow local Python execution testing
if __name__ == '__main__':
    lambda_handler(None,None)
