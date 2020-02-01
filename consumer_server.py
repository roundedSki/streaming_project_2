import asyncio

from confluent_kafka import Consumer
from confluent_kafka.admin import AdminClient


BROKER_URL = "PLAINTEXT://localhost:9092"


async def consume(topic_name):
    """Consumes data from the Kafka Topic"""
    c = Consumer({"bootstrap.servers": BROKER_URL, "group.id": "0"})
    c.subscribe([topic_name])
    while True:
        message = c.poll(1.0)
        if message is None:
            print("no message received by consumer")
        elif message.error() is not None:
            print(f"error from consumer {message.error()}")
        else:
            print(f"consumed message {message.key()}: {message.value()}")
        await asyncio.sleep(2.5)

        
async def consume_task(topic_name):
    """Runs the Consumer tasks"""
    t2 = asyncio.create_task(consume(topic_name))
    await t2



def main():
    topic_name = "sf_crime_topic"
    try:
        asyncio.run(consume_task(topic_name))
    except KeyboardInterrupt as e:
        print("shutting down")

if __name__ == "__main__":
    main()
