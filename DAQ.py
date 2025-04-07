import paho.mqtt.client as mqtt
import nidaqmx
import threading
import time
import numpy as np

class Daq:
    def __init__(self, client_id, broker_address, channel="Dev1/ai0"):
        self.client_id = client_id
        self.broker_address = broker_address
        self.channel = channel
        self.client = mqtt.Client(client_id)
        self.first_message_received = False
        self.running = False

        # Set callbacks for MQTT
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        # NI-DAQmx Task initialization (but not started)
        self.task = nidaqmx.Task()
        self.task.ai_channels.add_ai_voltage_chan(self.channel)

    def connect(self):
        try:
            print(f"[MQTT] Connecting to {self.broker_address}...")
            self.client.connect(self.broker_address)
            self.client.loop_start()  # Start the MQTT loop in a background thread
            print("[MQTT] Connected.")
            return True
        except Exception as e:
            print(f"[MQTT] Error: {e}")
            return False

    def subscribe(self, topic):
        try:
            self.client.subscribe(topic)
            print(f"[MQTT] Subscribed to topic: {topic}")
        except Exception as e:
            print(f"[MQTT] Subscribe failed: {e}")

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("[MQTT] Connected successfully")
        else:
            print(f"[MQTT] Connection failed with code {rc}")

    def on_message(self, client, userdata, message):
        if message.topic == "Sampling":
            command = message.payload.decode().strip().lower()
            if command == "start" and not self.sampling:
                self.start_sampling()
            elif command == "stop" and self.sampling:
                self.stop_sampling()

    def publish(self, topic, message):
        try:
            self.client.publish(topic, message)
            print(f"[MQTT] Published message: {message}")
        except Exception as e:
            print(f"[MQTT] Publish failed: {e}")

    def start_sampling(self):
        print("[Daq] Starting sampling at 30 Hz...")
        self.running = True
        self.sample_thread = threading.Thread(target=self.sampling_loop)
        self.sample_thread.start()

    def stop_sampling(self):
        print("[Daq] Stopping sampling...")
        self.running = False
        if self.sample_thread.is_alive():
            self.sample_thread.join()
        self.task.stop()
        print("[Daq] Sampling stopped.")

    def sampling_loop(self):
        # Configure the sampling rate to sample 33 values every 1/30 of a second
        self.task.timing.cfg_samp_clk_timing(30.0, samps_per_chan=33, sample_mode=nidaqmx.constants.AcquisitionType.FINITE)
        
        # Begin sampling
        self.task.start()

        while self.running:
            # Read 33 samples from the DAQ channel (A0) at once
            data = self.task.read(number_of_samples_per_channel=33)
            print(f"[Daq] Sampled data: {data}")

            # Publish the sampled data to MQTT
            self.publish("daq/data", f"Sampled: {data}")
            
            # Wait until 33 samples are acquired before starting the next cycle
            self.task.wait_until_task_done(timeout=2.0)  # Adjust timeout as needed


    def stop(self):
        self.stop_sampling()
        self.client.disconnect()
        print("[MQTT] Disconnected.")
