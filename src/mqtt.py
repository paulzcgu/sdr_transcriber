#!/usr/bin/env python
# -*- coding: utf-8 -*-
from queue import Queue

import logging
import paho.mqtt.client as paho

logger = logging.getLogger()


class MQTT_client():
    def __init__(self, host, taskQueue=None):
        self._client = None
        if (host):
            self.init_mqtt(host)

        if (taskQueue):
            self._taskQueue = taskQueue
        else:
            self._taskQueue = Queue()

    def init_mqtt(self, host, port=1883):
        self._client = paho.Client()
        self._client.on_message = self._on_message
        self._client.on_publish = self._on_publish
        self._client.connect(host, port, 30)
        logger.info("MQTT Client Initialized")

    def subscribe(self, topic):
        self._client.subscribe(topic)

    def run(self):
        logger.debug("MQTT Subscriber Started")
        self._client.loop_start()

    def _on_message(self, mosq, obj, msg):
        if (msg.payload):
            logger.debug("Task received from topic {}: {}"
                         .format(msg.topic, msg.payload))
        # DO SOMETHING
        self._taskQueue.put(msg.payload)

    def getNextTask(self):
        return self._taskQueue.get()

    def _on_publish(self, mosq, obj, mid):
        pass
