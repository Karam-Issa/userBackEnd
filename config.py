import asyncio


# env Variable

KAFKA_BOOTSTRAP_SERVERS = "localhost:9093"
KAFKA_TOPIC_POST = "postTopic"
KAFKA_CONSUMER_GROUP_POST = "postMicroservice"
KAFKA_TOPIC_USER = "userStatsTopic"
KAFKA_CONSUMER_GROUP_USER = "userMicroservice"

loop = asyncio.get_event_loop()