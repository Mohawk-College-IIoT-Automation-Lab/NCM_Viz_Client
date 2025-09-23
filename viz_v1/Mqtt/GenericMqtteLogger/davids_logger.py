"""
This module adds a MQTT handler to the basic logging module.
From there on, the basic logging module can be used, and everything will be logged to MQTT.
Formatting has also been updated accordingly the the following format:
    {
        "timestamp": "2023-10-01 12:00:00",
        "level": "INFO",
        "message": "System initialized successfully.",
        "process": "example_process"
        "error_code": 3003
    }

To use the error_code field, add it to the log record using the extra parameter:
    logging.error("Message 3: Failed to connect to the database.", extra={"error_code": 3003})

Information on overriding the logging handler can be found here:
https://docs.python.org/3/library/logging.html#logging.Handler
https://docs.python.org/3/library/logging.html#logging.Handler.emit

To Do:
- Handle MQTT connection errors more gracefully.
- Used the file name instead of a custom process name.
- The error message is not included in standard output, only in MQTT.
"""

import json
import logging
import paho.mqtt.client as mqtt
import time
import threading
import asyncio

SETUP_DELAY = 1
HEARTBEAT_PERIOD = 10


class MQTTHandler(logging.Handler):
    def __init__(self, process_name:str, broker:str, port:int, system_name:str="global"):
        super().__init__()
        self.broker = broker
        self.port = port
        self.process_name = process_name
        self.system_name = system_name
        self.topic = f"logs/{self.system_name}/{self.process_name}"
        self.heartbeat_topic = f"heartbeat/{self.system_name}/{self.process_name}"
        self.client = mqtt.Client()
        self.client.on_disconnect = self._on_disconnect
        self._connect_to_broker()
        self._start_heartbeat()

    def _connect_to_broker(self):
        def connect():
            while True:
                try:
                    self.client.connect(host=self.broker, port=self.port)
                    self.client.loop_start()
                    break
                except Exception as e:
                    logging.error(f"Failed to connect to MQTT broker: {e}")
                    logging.info("Retrying connection in 5 seconds...")
                    time.sleep(5)

        threading.Thread(target=connect, daemon=True).start()

    def _on_disconnect(self, client, userdata, rc):
        logging.warning("Disconnected from MQTT broker.")
        logging.info("Attempting to reconnect in 5 seconds...")
        threading.Thread(target=self._connect_to_broker, daemon=True).start()

    def _start_heartbeat(self):
        async def send_heartbeat():
            while True:
                heartbeat_message = {
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "process": self.process_name,
                    "status": "alive",
                }
                try:
                    self.client.publish(
                        self.heartbeat_topic, json.dumps(heartbeat_message)
                    )
                except Exception as e:
                    logging.error(
                        f"Failed to publish heartbeat to MQTT topic {self.heartbeat_topic}: {e}"
                    )
                await asyncio.sleep(HEARTBEAT_PERIOD)

        threading.Thread(
            target=lambda: asyncio.run(send_heartbeat()), daemon=True
        ).start()

    def emit(self, record):
        record.message = record.getMessage()
        log_entry = {
            "timestamp": self.formatter.formatTime(record, datefmt="%Y-%m-%d %H:%M:%S"),
            "level": record.levelname,
            "message": record.message,
            "process": self.process_name,
        }

        if hasattr(record, "error_code"):
            log_entry["error_code"] = record.error_code

        try:
            self.client.publish(self.topic, json.dumps(log_entry))
        except Exception as e:
            print(f"Failed to publish to MQTT topic {self.topic}: {e}")


class CustomFormatter(logging.Formatter):
    def format(self, record):
        level = f"{record.levelname:<8}"
        error_code = f"{getattr(record, 'error_code', ' '):<10}"
        formatted_message = f"{level} {error_code} {record.msg}"
        record.msg = formatted_message
        return super().format(record)


def initialize_logging(
    process_name,
    broker="localhost",
    port=1883,
    log_level=logging.DEBUG,
    system_name="global",
):
    """
    Initializes the logging system with MQTT and file handlers.

    Parameters:
    - process_name (str): The name of the process or application using the logger. This is used to identify the source of the logs.
    - broker (str): The MQTT broker address. Defaults to "localhost".
    - port (int): The port number for the MQTT broker. Defaults to 1883.
    - log_level (int): The logging level (e.g., logging.INFO, logging.DEBUG). Defaults to logging.INFO.
    - system_name (str): The system name or identifier. This is used as the root of the MQTT topic to avoid conflicts when multiple systems are on the same network. Defaults to "global".

    Details:
    - This function sets up logging to both MQTT and a local file. Logs are published to an MQTT topic structured as "system_name/process_name/logs".
    - A heartbeat message is also sent periodically to the topic "system_name/process_name/heartbeat" to indicate the process is alive.
    - The function introduces a short delay (1 second) after setup to ensure the logger is fully initialized before use.

    Note:
    - The `process_name` and `system_name` parameters are critical for ensuring unique MQTT topics, especially in environments with multiple systems or processes.
    - The delay is necessary to allow the MQTT client to establish a connection and start its loop.
    """
    log_file = f"{process_name}.log"
    logger = logging.getLogger()
    if not logger.handlers:
        mqtt_handler = MQTTHandler(
            process_name=process_name, broker=broker, port=port, system_name=system_name
        )
        formatter = CustomFormatter("%(asctime)s %(message)s")

        mqtt_handler.setFormatter(formatter)
        logger.addHandler(mqtt_handler)

        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        # Give the logger sometime to set up
        time.sleep(SETUP_DELAY)
    logger.setLevel(log_level)
