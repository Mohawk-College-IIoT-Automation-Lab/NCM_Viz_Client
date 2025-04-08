import nidaqmx
import time
import threading
import paho.mqtt.client as mqtt
import csv

class Daq:
    def __init__(self, mqtt_host = "localhost", mqtt_port = 1883):
        self.mqtt_host = mqtt_host
        self.mqtt_port = mqtt_port
        self.file_name = ""
        self.thread_running = False
        self.mqtt_client = mqtt.Client()
        self.daq_task = nidaqmx.Task()
        self.sampling_thread = threading.Thread(target=self.sampling_loop)

    def mqtt_connect(self):
        try:
            print(f"[MQTT] Connecting to {self.mqtt_host}...")
            self.mqtt_client.connect(self.mqtt_host)
            self.mqtt_client.loop_start()

            self.mqtt_subscribe("Sampling")
            self.mqtt_subscribe("Filename")

            return True
        except Exception as e:
            print(f"[MQTT] Connection error: {e}")
            return False

    def samplingCTL_start(self):
        self.thread_running = True
        self.sampling_thread = threading.Thread(target=self.sampling_loop)
        self.sampling_thread.start()
        print(f"[SamplingCTL] Starting sampling")

    def samplingCTL_stop(self):
        self.thread_running = False
        if self.sampling_thread.is_alive():
            self.sampling_thread.join()
        self.daq_task.stop()
        print(f"[SamplingCTL] Stopping sampling")

    def file_open(self):
        # Open the file for CSV output if a file name is given
        print(f"[File I/O] Trying to open file {self.file_name}")
        if self.file_name:
            self.file_handle = open(self.file_name, 'w', newline='')
            self.csv_writer = csv.writer(self.file_handle)
            # Write CSV header (if desired)
            self.csv_writer.writerow(['Channel 0', 'Channel 1'])  # Add more channels if needed
            print(f"[File I/O] File open {self.file_name}")
            return True
        else:
            self.file_handle = None
            print(f"[File I/O] No file name provided")
            return False

    def file_close(self):
        if self.file_handle:
            self.file_handle.close()
        print(f"[File I/O] Closing file {self.file_name}")

    def mqtt_publish(self, topic, message):
        self.mqtt_client.publish(topic, message)
        print(f"[MQTT] Published to topic: {topic}, message: {message}")

    def mqtt_subscribe(self, topic):
        self.mqtt_client.subscribe(topic)
        print(f"[MQTT] Subscribed to topic: {topic}")

    def mqtt_on_connect(self, client, userdata, flags, rc):
        print(f"[MQTT] Connected with result code {rc}")

    def mqtt_on_message(self, client, userdata, message):
        if message.topic == "Sampling":
            command = message.payload.decode().strip().lower()
            if command == "start" and not self.sampling:
                self.samplingCTL_start()
            elif command == "stop" and self.sampling:
                self.samplingCTL_stop()
            else:
                self.mqtt_publish("Log", f"Unexpected response: {command} is not start or stop")

        # don't want to change names while the system is writing
        if message.topic == "Filename" and not self.sampling_thread.is_alive():
            self.file_name = message.payload.decode().strip().lower()
        else:
            self.mqtt_publish("Log", "Could not change file name, thread is still running, stop first")

    def sampling_loop(self):
        # Open the CSV, if no filename is given safely stop and return
        if not self.file_open():
            self.file_close()
            self.samplingCTL_stop()
            return 

        # Add the channels you need to sample (e.g., A0, A1)
        self.daq_task.ai_channels.add_ai_voltage_chan("Dev1/ai0")
        self.daq_task.ai_channels.add_ai_voltage_chan("Dev1/ai1")
        
        # Configure continuous sampling for multiple channels
        self.daq_task.timing.cfg_samp_clk_timing(
            rate=990.0,  # Sampling rate: 990 Hz
            sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS,
            samps_per_chan=990  # Buffer size: 1 second of data
        )
 
        # Start the task
        self.daq_task.start()

        try:
            while self.thread_running:
                # Read all available data from the DAQ buffer
                data = self.daq_task.read()

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

#test

def main():
    daq = Daq(mqtt_host="10.4.8.5", mqtt_port=1883)

    if not daq.mqtt_connect():
        return

    

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        daq.samplingCTL_stop()
        print("Exiting...")

if __name__ == "__main__":
    main()