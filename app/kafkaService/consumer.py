from kafka import KafkaConsumer
import json
import logging
import ssl


class KafkaReportConsumer:
    def __init__(self, topic: str, group_id: str,bootstrap_servers: str):
        # self.topic = topic
        # self.bootstrap_servers = bootstrap_servers
        context = ssl.create_default_context(
            purpose=ssl.Purpose.SERVER_AUTH,
            cafile="path/to/ca.pem/file"
        )

        context.load_cert_chain(
            certfile="path/to/cert/file",
            keyfile="path/to/key/file",
            password="changeit"
        )

        self.consumer = KafkaConsumer(
            topic,
            bootstrap_servers=bootstrap_servers,
            security_protocol="SSL",
            ssl_context=context,
            auto_offset_reset="earliest",
            enable_auto_commit=True,
            group_id="group_id",
            value_deserializer=lambda x: json.loads(x.decode("utf-8")),
            request_timeout_ms=60000,
            session_timeout_ms=45000,
            retry_backoff_ms=500,
            reconnect_backoff_ms=500,
            reconnect_backoff_max_ms=10000
        )
        logging.info(f"Kafka consumer initialized for topic: {topic}")

    def listen(self,callback):
        print("Starting to listen for messages...")
        for message in self.consumer:
            try:
                print("message is -> ",message)
                data = message.value
                print(f"Received message: {data}")
                callback(data)
            except Exception as e:
                print(f"Error processing message: {e}")
