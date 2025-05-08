from kafka import KafkaProducer
import json
import logging
import ssl


class KafkaReportProducer:
    def __init__(self, topic: str,bootstrap_servers: str):
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
        self.producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            security_protocol="SSL",
            ssl_context=context,
            value_serializer=lambda x: json.dumps(x).encode("utf-8")
        )
        self.topic = topic
        logging.info(f"Kafka consumer initialized for topic: {topic}")

    def produce_email_payload(self,payload: dict):
        logging.info("Starting to send messages...")
        self.producer.send(self.topic, value=payload)
        self.producer.flush()
        logging.info(f"Sent message: {payload}")

