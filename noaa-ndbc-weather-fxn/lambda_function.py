# Generate RTS data for Forecast of SatCom Mhz usage by spot-beam
# Parse NOAA NDBC (buoy data) to get air-pressure readings
# Send o/p to file in format timestamp, air-pressure, spotbeam, day-of-week, hour-of-day

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



numRecs = 144 * 14       # TTS data : 14d
horizonRecs = 144        # RTS forecast : 1d (10 min granularity : 6 * 24)
numHdrRows = 2           # skip the 2 header rows in ndbc data files 


def lambda_handler(event, context):

    # this can be run either as cmd line py program or a Lambda based on the execution environment    
    execEnv = str(os.getenv('AWS_EXECUTION_ENV'))
    if execEnv.startswith("AWS_Lambda"):
        bucketName = os.getenv('bucketName')
        ndbc = os.getenv('ndbc')
        spotBeam = os.getenv('spotBeam')
    else:
        parser = argparse.ArgumentParser()
        parser.add_argument("-b", "--bucketname", help="This bucket will hold the Forecast Weather data")
        parser.add_argument("-n", "--ndbc", help="The most recent NDBC buoy data file by station id")
        parser.add_argument("-s", "--spotBeam", help="Append the spotBeam name to the RTS output file")
        args = parser.parse_args()
        bucketName = args.bucketname
        ndbc = args.ndbc
        spotBeam = args.spotBeam

    if None in (bucketName, ndbc, spotBeam):
        print("Invalid bucketName or ndbc file and/or output files")
        return -1
    else:
        print("Bucket: ", bucketName, " Buoy file: ", ndbc, " Spot Beam: ", spotBeam)

    # read in the ndbc data file (txt)
    with open(ndbc) as f_ndbc:
        lines = f_ndbc.readlines()

    rts_records = []
    for i in range(numHdrRows, numRecs + horizonRecs + numHdrRows):

        fields = lines[i].split()
        
        # construct datetime in format Amazon Forecast wants YYYY-MM-DD hh:mm:ss
        dt = fields[:5]
        dt_fmt = dt[0] + '-' + dt[1] + '-' + dt[2] + ' ' + dt[3] + ':' + dt[4] + ':00'

        # now retrieve the air-pressure in hPa - change missing entries 'MM' to empty
        # since Amazon Forecast can fill them in
        airpressure = fields[12]
        if airpressure == 'MM':
            airpressure = ''
        
        # construct the rts_record
        rts_rec = {}
        rts_rec['timestamp'] = dt_fmt
        rts_rec['airpressure'] = airpressure
        rts_rec['beam'] = spotBeam
        rts_rec['dayofweek'] = fields[2]
        rts_rec['hourofday'] = fields[3]

        rts_records.append(rts_rec)

    rts_recs = fmt_rts_recs(rts_records)
    
    # put TTS and RTS in separate folders for simpler BI tools (eg QuickSight) ingest
    put_object(bucketName, "dataset/rts/", rts_recs, "rts-weather", spotBeam)
    
    
    return None



# helper functions...
# format RTS record entries
def fmt_rts_recs(recs):
    
    rts_str = ""
    for i in range(len(recs)):
        rts_str = rts_str + str(recs[i]['timestamp']) + "," + str(recs[i]['airpressure']) + "," + \
        recs[i]['beam'] + "," + str(recs[i]['dayofweek']) + "," + str(recs[i]['hourofday']) + "\n"
        
    return rts_str


# function to put an object into S3 bucket
def put_object(bucket, key, data, filename, beam):
    
    dt_1 = datetime.now()
    dt_secs = int(dt_1.timestamp())

    f_name = os.path.splitext(filename)[0]
    f_name = f_name + "_" + beam + "_" + str(dt_secs) + ".csv"
    
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
