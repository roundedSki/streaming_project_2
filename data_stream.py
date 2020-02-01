import logging
import json
from pyspark.sql import SparkSession
from pyspark.sql.types import *
import pyspark.sql.functions as psf
import time


# TODO Create a schema for incoming resources
schema = StructType([StructField("crime_id", StringType(), True),
                     StructField("original_crime_type_name", StringType(), True),
                     StructField("report_date", StringType(), True),
                     StructField("call_date", StringType(), True),
                     StructField("offense_date", StringType(), True),
                     StructField("call_time", StringType(), True),
                     StructField("call_date_time", StringType(), True),
                     StructField("disposition", StringType(), True),
                     StructField("address", StringType(), True),
                     StructField("city", StringType(), True),
                     StructField("state", StringType(), True),
                     StructField("agency_id", StringType(), True),
                     StructField("address_type", StringType(), True),
                     StructField("common_location", StringType(), True)
                     ])

def run_spark_job(spark):

    # TODO Create Spark Configuration
    # Create Spark configurations with max offset of 200 per trigger
    # set up correct bootstrap server and port
    df = spark \
        .readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "localhost:9092") \
        .option("subscribe", "sf_crime_topic") \
        .option("startingOffsets", "earliest") \
        .option("maxOffsetsPerTrigger", 200) \
        .option("maxRatePerPartition", 200) \
        .option("stopGracefullyOnShutdown", "true") \
        .load()


    # Show schema for the incoming resources for checks
    df.printSchema()

    # TODO extract the correct column from the kafka input resources
    # Take only value and convert it to String
    kafka_df = df.selectExpr("CAST(value AS STRING)")

    service_table = kafka_df\
        .select(psf.from_json(psf.col('value'), schema).alias("DF"))\
        .select("DF.*")

    # TODO select original_crime_type_name and disposition
    distinct_table = service_table.select("original_crime_type_name",
                                          "disposition") #.distinct()

    # count the number of original crime type
    agg_df = service_table.filter("original_crime_type_name is not null") \
                           .groupBy("original_crime_type_name", "disposition") \
                           .agg(psf.count("*").alias("count_original_Crime_Type")) \
                           .orderBy(psf.col("count_original_Crime_Type").desc())

    # TODO Q1. Submit a screen shot of a batch ingestion of the aggregation
    # TODO write output stream
    query = agg_df \
        .writeStream \
        .trigger(processingTime="20 seconds") \
        .outputMode('Complete') \
        .format('console') \
        .queryName("sf_original_crime_typeg") \
        .start()

    # TODO attach a ProgressReporter
    query.awaitTermination()

    # TODO get the right radio code json path
    radio_code_json_filepath = "radio_code.json"
    radio_code_df = spark.read.option("multiline", "true").json(radio_code_json_filepath)

    # clean up your data so that the column names match on radio_code_df and agg_df
    # we will want to join on the disposition code
    #agg_df = agg_df.join(distinct_table, "original_crime_type_name")

    # TODO rename disposition_code column to disposition
    radio_code_df = radio_code_df.withColumnRenamed("disposition_code", "disposition")

    # TODO join on disposition column
    joined_crime_code_df = agg_df.join(radio_code_df, "disposition", "left_outer")
    join_query = joined_crime_code_df \
                 .writeStream \
                 .format('console') \
                 .trigger(processingTime="20 seconds") \
                 .queryName("sf_original_crime_code_count") \
                 .outputMode('Complete') \
                 .start()
    
    join_query.awaitTermination()


if __name__ == "__main__":
    logger = logging.getLogger(__name__)

    # TODO Create Spark in Standalone mode
    spark = SparkSession \
        .builder \
        .master("local[*]") \
        .appName("KafkaSparkStructuredStreaming") \
        .getOrCreate()

    logger.info("Spark started")

    #spark.sparkContext.setLogLevel("WARN")

    run_spark_job(spark)

    spark.stop()
