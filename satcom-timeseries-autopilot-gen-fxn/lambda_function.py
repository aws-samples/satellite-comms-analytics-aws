# Generate unified timeseries CSV for Sagemaker Autopilot Satcom Forecast of SatCom Mhz usage by spot-beam
# Unlike Amazon Forecast, Sagemaker Autopilot requires all fields in 1 file (metadata, covariates & target)
# For best AutoPredictor results future-dated (to end of time horizon) coviarates & metadata is recommended

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
startmonth = 6
startday = 1

spotBeamsTrain = ['SpotH3', 'SpotH7', 'SpotH12', 'SpotH15']
spotBeamsInf = ['SpotH12']

nRecs = 144 * 14         # TTS data : 14d
horizonRecs = 144        # RTS forecast : 1d (10 min granularity : 6 * 24)


def lambda_handler(event, context):

    # this can be run either as cmd line py program or a Lambda based on the execution environment    
    execEnv = str(os.getenv('AWS_EXECUTION_ENV'))
    if execEnv.startswith("AWS_Lambda"):
        bucketName = os.getenv('bucketName')
        timeseriesSatCom = os.getenv('timeseriesSatCom')
        mode = os.getenv('mode')
    else:
        parser = argparse.ArgumentParser()
        parser.add_argument("-b", "--bucketname", help="This bucket will hold the Forecast input data")
        parser.add_argument("-t", "--timeseriesSatCom", help="This file will be generated with SatCom usage")
        parser.add_argument("-m", "--mode", help="generate Training or Real-Time Inference input data")
        args = parser.parse_args()
        bucketName = args.bucketname
        timeseriesSatCom = args.timeseriesSatCom
        mode = args.mode

    if None in (bucketName, timeseriesSatCom, mode):
        print("Invalid bucketName and/or generated files and/or mode selection")
        return -1
    else:
        print("Bucket: ", bucketName, " SatCom Timeseries file: ", timeseriesSatCom, "Mode: ", mode)
        
    # check that mode is either 'train' or 'inf'
    if mode not in ['train', 'inf']:
        print("Invalid mode selection - must be train or inf")
        return -1

    # set up the params for Train or Real Time Inference mode
    # RT Inf is a subset of the Train data on a particular item_id
    if mode == 'train':
        spotBeams = spotBeamsTrain
        numRecs = nRecs
    else:
        spotBeams = spotBeamsInf
        numRecs = nRecs // 4

    # set the initial date/time for the TTS dataset
    initDate = datetime(startyear, startmonth, startday)
    print (initDate)

    satcom_records = []
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
        
            satcom_rec = {}
            satcom_rec['timestamp'] = ts
            satcom_rec['beam'] = b
            satcom_rec['dayofweek'] = day_of_week
            satcom_rec['hourofday'] = hr

            # target variable is obviously NOT future-dated
            if i < numRecs:
                if satcom_rec['beam'] == 'SpotH7':
                    satcom_rec['mHz'] = random.randint(250,300)
                else:
                    satcom_rec['mHz'] = random.randint(200,250)
                satcom_rec['mHz'] = satcom_rec['mHz'] * surgeMultiplier
            
            # weather covariate IS future-dated
            if satcom_rec['beam'] == 'SpotH12' and hr in range(6,9):
                satcom_rec['airpressure'] = random.randint(950,1000)
                if i < numRecs:
                    satcom_rec['mHz'] = satcom_rec['mHz'] * weatherMultiplier
            else:
                satcom_rec['airpressure'] = random.randint(1000,1050)
            
            satcom_records.append(satcom_rec)
        
        # increment date by 10 mins for next mHz datapoint
        ts = ts + timedelta(minutes=10)
            
    
    satcom_recs = fmt_satcom_recs(satcom_records)

    # put unified timeseries data in bucket
    if mode == 'train':
        put_object(bucketName, "dataset/train/", satcom_recs, timeseriesSatCom)
    else: 
        put_object(bucketName, "dataset/rtinf/", satcom_recs, timeseriesSatCom)
    
    return None


# helper functions...

# format Satcom record entries
def fmt_satcom_recs(recs):
    
    ts_str = ""
    ts_str = ts_str + "timestamp,airpressure,beam,dayofweek,hourofday,mHz\n"
    for i in range(len(recs)):
        ts_str = ts_str + str(recs[i]['timestamp']) + "," + str(recs[i]['airpressure']) + "," + \
        recs[i]['beam'] + "," + str(recs[i]['dayofweek']) + "," + str(recs[i]['hourofday']) + "," 
        
        if 'mHz' in recs[i]:
            ts_str = ts_str + str(recs[i]['mHz'])
        
        ts_str = ts_str + "\n"
        
    return ts_str

    
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
