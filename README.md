# streaming_project_2

1.How did changing values on the SparkSession property parameters affect the throughput and latency of the data?
Answer: processedRowsperSecond -- it defines the throughput, and it should be more.
     Increasing the maxRatePerPartition increases the throughput and decreases latency while increasing processingTime does the opposite, in this case. As the processing time in this application should not be too high, as it processes the data quickly.
     We can also increase the kafka and spark partitions depending on the number of cores as they map one-to-one and it will increase parallelism and more records can be processed.

2. What were the 2-3 most efficient SparkSession property key/value pairs? Through testing multiple variations on values, how can you tell these were the most optimal?
Answer: The three most efficent SparkSession propertiy key/value pairs.
      1) spark.streaming.kafka.maxRatePerPartition - 
         On increasing this paramter, there was increase in data ingestion. It sets the maximum number of messages per partition per batch.
         It can be put to an optimal rate where all the messages can be processed in the processing time and there is no lag between receiving and processing of messages.

      2) spark.sql.shuffle.partitions"
         It helped in parallel processing of the data while join and other shuffle operations. Default is 200, but in case where we have a lot of data and then, increasing this will process data faster in more number of tasks. 

      3)  spark.executor.memory
         It will help in assigning appropriate memory to each executors to process the records. In case of out-of-memory issues, this can be used.
