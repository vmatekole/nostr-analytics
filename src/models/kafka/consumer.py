from confluent_kafka import Consumer, avro
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroDeserializer
from confluent_kafka.serialization import MessageField, SerializationContext

avro_deserializer = AvroDeserializer(
    SchemaRegistryClient(
        {
            'url': 'https://selected-alien-14337-eu2-rest-kafka.upstash.io/schema-registry',
            'basic.auth.user.info': 'c2VsZWN0ZWQtYWxpZW4tMTQzMzck8Hz7yBAMVN1ItkXS96W1R5A4ImWolGoXFW8:ZGE2MjZkMTItOWExYi00Y2ViLTk4YzAtMzc2YzRkYmJjODFm',
        }
    )
)

consumer = Consumer(
    {
        'bootstrap.servers': 'selected-alien-14337-eu2-kafka.upstash.io:9092',
        'sasl.mechanism': 'SCRAM-SHA-256',
        'security.protocol': 'SASL_SSL',
        'sasl.username': 'c2VsZWN0ZWQtYWxpZW4tMTQzMzck8Hz7yBAMVN1ItkXS96W1R5A4ImWolGoXFW8',
        'sasl.password': 'ZGE2MjZkMTItOWExYi00Y2ViLTk4YzAtMzc2YzRkYmJjODFm',
        'group.id': 'YOUR_CONSUMER_GROUP',
        'auto.offset.reset': 'earliest',
    }
)
consumer.subscribe(['YOUR_TOPIC'])

while True:
    msg = consumer.poll(1.0)
    if msg is None:
        continue

    deserialized = avro_deserializer(
        msg.value(), SerializationContext(msg.topic(), MessageField.VALUE)
    )
    if deserialized is not None:
        print('Key {}: Value{} \n'.format(msg.key(), deserialized))

consumer.close()
