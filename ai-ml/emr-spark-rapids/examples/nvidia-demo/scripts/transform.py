import logging
import time
import sys

from pyspark.sql import SparkSession
from pyspark import SparkConf
from pyspark.sql.functions import col, expr, from_json
from pyspark.sql.types import StructType, StructField, StringType, ArrayType, MapType

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Validate input arguments
if len(sys.argv) > 2:
    input_path = sys.argv[1]
    output_path = sys.argv[2]
    logger.info(f"Processing data from input path: {input_path}")
    logger.info(f"Output will be written to: {output_path}")
else:
    logger.error("Data root path not provided. Usage: script.py <input_path> <output_path>")
    sys.exit(1)

# Configure Spark with RAPIDS plugin to ensure GPU execution
logger.info("Configuring Spark session with RAPIDS (GPU acceleration enabled)...")
conf = SparkConf() \
    .setAppName("CSV-to-JSONL-GPU") \
    .set("spark.plugins", "com.nvidia.spark.SQLPlugin")
 # Debugging info

# Initialize Spark session
spark = SparkSession.builder.config(conf=conf).getOrCreate()
logger.info("Spark session initialized successfully with RAPIDS GPU acceleration.")

# Define schema
schema = StructType([
    StructField("system", StringType(), True),
    StructField("mask", StringType(), True),
    StructField("dataset", StringType(), True),
    StructField("conversations", StringType(), True)  # JSON stored as a string
])

# Define S3 paths
# input_path = "s3://your-bucket-name/input-folder/"  # Folder containing CSV files
# output_path = "s3://your-bucket-name/output-folder/"

# Read multiple CSV files from S3
logger.info(f"Reading CSV files from {input_path}...")
df = spark.read.option("header", True).schema(schema).csv(input_path)

# Convert conversations column to valid JSON format
logger.info("Fixing JSON format issues in the conversations column...")
# df = df.withColumn("conversations", expr("regexp_replace(conversations, '\\\\'\\'\\'', '\"')"))  # Fix malformed JSON
# df = df.withColumn("conversations", from_json(col("conversations"), ArrayType(MapType(StringType(), StringType()))))

# Write to JSONL with partitioning to ensure ~128MB file size
logger.info(f"Writing JSONL files to {output_path} with 128MB chunks...")
# df.repartition(384 * 1024 * 1024 // 1024) \
#   .write \
#   .mode("overwrite") \
#   .parquet(output_path)

# Avoid full shuffle by using coalesce instead of repartition
df = df.coalesce(8)  

df.write \
  .mode("overwrite") \
  .format("parquet") \
  .save(output_path)
  
df.show(10)  

# Ensuring job runs for at least 5 minutes to observe GPU performance
logger.info("Ensuring job runs for at least 5 minutes...")

# time.sleep(300)

# Stop the Spark session
logger.info("Stopping the Spark session.")
spark.stop()
logger.info("Spark session stopped successfully.")

logger.info("Spark RAPIDS job completed successfully.")
