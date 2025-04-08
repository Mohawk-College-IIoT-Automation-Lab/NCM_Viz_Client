import nidaqmx
import time
import threading
import paho.mqtt.client as mqtt
import csv

class Daq:
    def __init__(self, mqtt_host, mqtt_port, mqtt_topic, file_name=None):
        self.mqtt_host = mqtt_host
        self.mqtt_port = mqtt_port
        self.mqtt_topic = mqtt_topic
        self.file_name = file_name
        self.running = False
        self.client = mqtt.Client()
        
        # Open the file for CSV output if a file name is given
        if self.file_name:
            self.file_handle = open(self.file_name, 'w', newline='')
            self.csv_writer = csv.writer(self.file_handle)
            # Write CSV header (if desired)
            self.csv_writer.writerow(['Channel 0', 'Channel 1'])  # Add more channels if needed
        else:
            self.file_handle = None

        # Initialize DAQ task
        self.task = nidaqmx.Task()
        self.thread = threading.Thread(target=self.sampling_loop)

    def mqtt_connect(self):
        try:
            print(f"[MQTT] Connecting to {self.mqtt_host}...")
            self.client.connect(self.mqtt_host)
            self.client.loop_start()
            return True
        except Exception as e:
            print(f"[MQTT] Connection error: {e}")
            return False

    def samplingCTL_start(self):
        self.running = True
        self.thread = threading.Thread(target=self.sampling_loop)
        self.thread.start()

    def samplingCTL_stop(self):
        self.running = False
        if self.thread.is_alive():
            self.thread.join()
        self.task.stop()

    def file_close(self):
        if self.file_handle:
            self.file_handle.close()

    def mqtt_publish(self, topic, message):
        self.client.publish(topic, message)
        print(f"[MQTT] Published to topic: {topic}, message: {message}")

    def mqtt_subscribe(self, topic):
        self.client.subscribe(topic)
        print(f"[MQTT] Subscribed to topic: {topic}")

    def mqtt_on_connect(self, client, userdata, flags, rc):
        print(f"[MQTT] Connected with result code {rc}")

    def mqtt_on_message(self, client, userdata, message):
        if message.topic == "Sampling":
            command = message.payload.decode().strip().lower()
            if command == "start" and not self.sampling:
                self.start()
            elif command == "stop" and self.sampling:
                self.samplingCTL_stop()     

    def sampling_loop(self):
        # Add the channels you need to sample (e.g., A0, A1)
        self.task.ai_channels.add_ai_voltage_chan("Dev1/ai0")
        self.task.ai_channels.add_ai_voltage_chan("Dev1/ai1")
        
        # Configure continuous sampling for multiple channels
        self.task.timing.cfg_samp_clk_timing(
            rate=990.0,  # Sampling rate: 990 Hz
            sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS,
            samps_per_chan=990  # Buffer size: 1 second of data
        )

        # Start the task
        self.task.start()

        try:
            while self.running:
                # Read all available data from the DAQ buffer
                data = self.task.read()

                if not data:
                    continue  # If no data, skip this loop iteration

                # data[0] -> channel A0 samples, data[1] -> channel A1 samples
                message = ",".join(f"{x:.6f}" for x in data[0]) + "," + ",".join(f"{x:.6f}" for x in data[1])

                # Publish the data to MQTT
                self.mqtt_publish(self.mqtt_topic, message)

                # Write the data to the file
                if self.file_handle:
                    self.csv_writer.writerow(data[0] + data[1])  # Flatten and write to CSV file
                    self.file_handle.flush()

        except Exception as e:
            print(f"[DAQ] Sampling error: {e}")

        finally:
            # Stop the task when done
            self.file_close()
            self.samplingCTL_stop()


def main():
    daq = Daq(client_id="myDaqClient", broker_address="localhost")

    if not daq.mqtt_connect():
        return

    daq.mqtt_subscribe("Sampling")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        daq.samplingCTL_stop()
        print("Exiting...")

if __name__ == "__main__":
    main()