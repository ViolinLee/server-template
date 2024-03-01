import json
import socket
import datetime
import threading
from kafka import KafkaProducer


class KafkaLogger(KafkaProducer):

    def __init__(self, server, topic):
        super().__init__(bootstrap_servers=server)
        self.topic = topic
        self.threadId = threading.get_ident()
        self.k8s_pod_name = socket.gethostname()

    def format_log(self, class_name, method_name, level, msg):
        formated = {
            "threadId": self.threadId,
            "create_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"),
            "method": method_name,
            "level": level,
            "topic": self.topic,
            "k8s_pod_name": self.k8s_pod_name,
            "source": "LOGBEAT2.0",
            "class": class_name,
            "msginfo": msg
        }

        return formated

    def info(self, msg):
        payload = self.format_log('ScheduleCal', 'post', 'INFO', msg)
        self.send(self.topic, json.dumps(payload).encode("utf-8"))

    def error(self, msg):
        payload = self.format_log('ScheduleCal', 'post', 'ERROR', msg)
        self.send(self.topic, json.dumps(payload).encode("utf-8"))
