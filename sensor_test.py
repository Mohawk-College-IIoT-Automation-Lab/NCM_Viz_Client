import nidaqmx  # Library for interfacing with NI DAQ devices
import time  # For sleep and timing operations
import numpy as np  # For numerical operations
import math  # For mathematical operations
import threading  # For multithreading (not used in this code)

from nidaqmx.constants import FilterType, AcquisitionType, LoggingMode, LoggingOperation, READ_ALL_AVAILABLE

# Constants for DAQ configuration
SAMPLE_RATE = 1000  # Sampling rate in Hz
SAMPLES_PER_READ = 1000  # Number of samples to read per channel
OUTPUT_FREW = 10000  # (Unused in this code)
CHANNELS = ["Dev2/ai0", "Dev2/ai1", "Dev2/ai2", "Dev2/ai3"]  # List of analog input channels
FILE_NAME = "daq_data.tdms"  # File name for logging data

# Create a global task object for the DAQ
task = nidaqmx.Task()

def main():
    # Set up the first analog input channel
    channel = task.ai_channels.add_ai_voltage_chan(CHANNELS[0])

    # Optional: Configure a digital filter for the channel (currently commented out)
    # channel.ai_dig_fltr_enable = True
    # channel.ai_dig_fltr_lowpass_cutoff_freq = 1000  # Low-pass filter cutoff frequency in Hz
    # channel.ai_dig_fltr_type = FilterType.LOWPASS  # Filter type

    # Configure the sampling clock timing for continuous acquisition
    task.timing.cfg_samp_clk_timing(
        rate=SAMPLE_RATE,  # Sampling rate in Hz
        sample_mode=AcquisitionType.CONTINUOUS,  # Continuous sampling mode
        samps_per_chan=SAMPLES_PER_READ  # Number of samples per channel
    )

    # Configure logging to save data to a TDMS file
    task.in_stream.configure_logging(
        file_path=FILE_NAME,  # Path to the TDMS file
        logging_mode=LoggingMode.LOG_AND_READ,  # Log data and allow reading
        operation=LoggingOperation.CREATE_OR_REPLACE  # Create or overwrite the file
    )

    print("Starting data collection. Press Ctrl+C to stop.")
    task.start()  # Start the DAQ task

    # Infinite loop to continuously read and process data
    while True:
        try:
            # Read all available data from the task
            data = task.read(READ_ALL_AVAILABLE)
            
            # Calculate the average of the data
            avg = np.average(np.array(data))
            if not math.isnan(avg):  # Check if the average is a valid number
                print(f"Sampled {SAMPLES_PER_READ} at {SAMPLE_RATE} Hz avg value: {avg}")
        except Exception as e:
            # Handle any exceptions that occur during data reading
            print(f"[Error] {e}")

if __name__ == "__main__":
    # Run the main function
    main()
    try:
        # Keep the program running until interrupted
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        # Handle Ctrl+C to gracefully exit the program
        print("Exiting...")
        task.stop()  # Stop the DAQ task