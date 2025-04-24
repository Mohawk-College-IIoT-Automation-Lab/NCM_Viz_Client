from paho.mqtt.client import Client, MQTTMessage
import logging


class M_Object:
    def __init__(self, host_name:str="localhost", host_port:int = 1883, log_name="log"):
      
        self.logger = logging.getLogger(log_name)
        self.logger.setLevel(logging.DEBUG)
        
        file_handler = logging.FileHandler(f"{log_name}.log")
        file_handler.setLevel(logging.DEBUG)

        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)

        self.logger.addHandler(file_handler)
        self.log("Logging initialized")

        self._connected = False
        self._host_name = host_name
        self._host_port = host_port
        self.mqtt_client = Client()

        self.mqtt_client.on_message = self._mqtt_default_callback
        self.mqtt_client.on_connect = self._mqtt_connect_disconnect
        self.mqtt_client.on_disconnect = self._mqtt_connect_disconnect
        self.mqtt_client.on_connect_fail = self._mqtt_failed

    def _mqtt_connect_disconnect(self):
        # Get connection status
        self._connected = self.mqtt_client.is_connected()
        
        # Loop start/stop
        if self._connected:
            self.mqtt_client.loop_start()
        else:
            self.mqtt_client.loop_stop()

        # Loggign and emit status
        self.log(f"[MQTT] Connection status: {self.connected}")
        
    def _mqtt_failed(self):
        self._connected = self.mqtt_client.is_connected()
        self.mqtt_client.loop_stop()
        self.log("[MQTT] Failed to connect")

    def _mqtt_default_callback(self, client:Client, userdata, message:MQTTMessage):
        self.log(f"[MQTT] unhandled data received from topic: {message.topic} -> {message.payload.decode()}")

    def log(self, message:str):
        self.logger.debug(message)

    def mqtt_connect(self):
        self.log(f"[MQTT] Attempting connection to host: {self._host_name} on port: {self._host_port}")
        
        error = self.mqtt_client.connect(self._host_name, self._host_port)
        if error:
            self.log(f"[MQTT] Error connecting to host: {self._host_name}:{self._host_port}, error code: {error}")
            
        
    def mqtt_disconnect(self):
        self.log(f"Disconnecting from {self._host_name}:{self._host_port}")
        self.mqtt_client.disconnect()

    @property
    def connected(self):
        return self._connected

    @property
    def host_name(self):
        return self._host_name

    @host_name.setter
    def host_name(self, value: str):
        if self.connected:
            self.log("Cannot change host name while connected")
            return
        self._host_name = value

    @property
    def host_port(self):
        return self._host_port

    @host_port.setter
    def host_port(self, value: int):
        if self.connected:
            self.log("Cannot change host port while connected")
            return
        self._host_port = value