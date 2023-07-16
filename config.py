import asyncio


# env Variable

KAFKA_BOOTSTRAP_SERVERS = "localhost:9093"
KAFKA_TOPIC = "postTopic"
KAFKA_CONSUMER_GROUP = "postMicroservice"

loop = asyncio.get_event_loop()