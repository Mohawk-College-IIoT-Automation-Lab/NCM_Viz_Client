import nidaqmx  # Library for interfacing with NI DAQ devices
import time  # For sleep and timing operations
import numpy as np  # For numerical operations
import math  # For mathematical operations
import multiprocessing

from nidaqmx.constants import (
    FilterType,
    AcquisitionType,
    LoggingMode,
    LoggingOperation,
    READ_ALL_AVAILABLE,
)


class DAQ_Worker(multiprocessing.Process):

    # Constants for DAQ configuration
    SAMPLE_RATE = 1000  # Sampling rate in Hz
    SAMPLES_PER_READ = 1000  # Number of samples to read per channel
    OUTPUT_FREW = 10000  # (Unused in this code)
    CHANNELS = [
        "Dev2/ai0",
        "Dev2/ai1",
        "Dev2/ai2",
        "Dev2/ai3",
    ]  # List of analog input channels
    FILE_NAME = "daq_data.tdms"  # File name for logging data

    def __init__(
        self,
        channels: list = CHANNELS,
        sample_rate: int = SAMPLE_RATE,
        samples_per_read: int = SAMPLES_PER_READ,
        display_rate: int = 30,
        file_name: str = FILE_NAME,
    ):
        super().__init__(self)  # Initialize the proess

        self.channels = channels  # List of analog input channels
        self.sample_rate = sample_rate  # Sampling rate in Hz
        self.display_rate = display_rate
        self.samples_per_read = samples_per_read  # Number of samples to read per channel
        self.file_name = file_name  # File name for logging data

        self.task = nidaqmx.Task()  # Create a global task object for the DAQ
        self.running = False  # Flag to control the thread execution

    def stop(self):
        self.running = False
        self.task.close()

    def run(self):
        channel = self.task.ai_channels.add_ai_voltage_chan(self.channels)

        # Optional: Configure a digital filter for the channel (currently commented out)
        # channel.ai_dig_fltr_enable = True
        # channel.ai_dig_fltr_lowpass_cutoff_freq = 1000  # Low-pass filter cutoff frequency in Hz
        # channel.ai_dig_fltr_type = FilterType.LOWPASS  # Filter type

        # Configure the sampling clock timing for continuous acquisition
        self.task.timing.cfg_samp_clk_timing(
            rate=self.SAMPLE_RATE,  # Sampling rate in Hz
            sample_mode=AcquisitionType.CONTINUOUS,  # Continuous sampling mode
            samps_per_chan=self.SAMPLES_PER_READ  # Number of samples per channel
        )

        # Configure logging to save data to a TDMS file
        self.task.in_stream.configure_logging(
            file_path=self.FILE_NAME,  # Path to the TDMS file
            logging_mode=LoggingMode.LOG_AND_READ,  # Log data and allow reading
            operation=LoggingOperation.CREATE_OR_REPLACE  # Create or overwrite the file
        )

        print("Starting data collection. Press Ctrl+C to stop.")
        self.task.start()  # Start the DAQ task

        # Infinite loop to continuously read and process data
        while self.running:
            try:
                # Read all available data from the task
                data = self.task.read(READ_ALL_AVAILABLE)
                
                # Calculate the average of the data
                avg = np.average(np.array(data))
                if not math.isnan(avg):  # Check if the average is a valid number
                    print(f"Sampled {self.SAMPLES_PER_READ} at {self.SAMPLE_RATE} Hz avg value: {avg}")
            except Exception as e:
                # Handle any exceptions that occur during data reading
                print(f"[Error] {e}")


if __name__ == '__main__':
    p1 = DAQ_Worker()

    try:
        # Keep the program running until interrupted
        p1.start()
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        # Handle Ctrl+C to gracefully exit the program
        print("Exiting...")
        p1.stop()
        p1.join()