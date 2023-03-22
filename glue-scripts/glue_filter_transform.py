import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
import re

# Configure required parameters
params = [
    'JOB_NAME',
    'input_gluedatabase',
    'input_gluetable',
    'output_gluedatabase',
    'output_gluetable',
    'output_path'
]

args = getResolvedOptions(sys.argv, params)
input_gluedatabase = args['input_gluedatabase']
input_gluetable = args['input_gluetable']
output_gluedatabase = args['output_gluedatabase']
output_gluetable = args['output_gluetable']
output_path = args['output_path']

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args["JOB_NAME"], args)

# Script generated for node S3 bucket
S3bucket_node1 = glueContext.create_dynamic_frame.from_catalog(
    database=input_gluedatabase,
    table_name=input_gluetable,
    transformation_ctx="S3bucket_node1",
)

# Script generated for node ApplyMapping
ApplyMapping_node2 = ApplyMapping.apply(
    frame=S3bucket_node1,
    mappings=[
        ("datetime", "string", "datetime", "timestamp"),
        ("remoteid", "string", "remoteid", "string"),
        ("beamid", "int", "beamid", "int"),
        ("beamname", "string", "beamname", "string"),
        ("satlong", "double", "satlong", "double"),
        ("fwdmodcodid", "int", "fwdmodcodid", "int"),
        ("fwdsnr", "double", "fwdsnr", "float"),
        ("packetslost", "int", "packetslost", "int"),
        ("latitude", "double", "latitude", "float"),
        ("longitude", "double", "longitude", "float"),
        ("rxfreq", "int", "rxfreq", "int"),
        ("txfreq", "int", "txfreq", "int"),
        ("fwdbitrate", "double", "fwdbitrate", "double"),
        ("year", "string", "year", "string"),
        ("month", "string", "month", "string"),
        ("day", "string", "day", "string"),
        ("hour", "string", "hour", "string"),
    ],
    transformation_ctx="ApplyMapping_node2",
)

# Script generated for node Filter
Filter_node1670204808887 = Filter.apply(
    frame=ApplyMapping_node2,
    f=lambda row: (bool(re.match("^C", row["remoteid"]))),
    transformation_ctx="Filter_node1670204808887",
)

# Script generated for node S3 bucket
S3bucket_node3 = glueContext.getSink(
    path=output_path,
    connection_type="s3",
    updateBehavior="UPDATE_IN_DATABASE",
    partitionKeys=["year", "month", "day", "hour"],
    enableUpdateCatalog=True,
    transformation_ctx="S3bucket_node3",
)
S3bucket_node3.setCatalogInfo(
    catalogDatabase=output_gluedatabase,
    catalogTableName=output_gluetable,
)
S3bucket_node3.setFormat("json")
S3bucket_node3.writeFrame(Filter_node1670204808887)
job.commit()
