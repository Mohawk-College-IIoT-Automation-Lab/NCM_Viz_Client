import nidaqmx  # Library for interfacing with NI DAQ devices
import time  # For sleep and timing operations
import nidaqmx.constants
import nidaqmx.stream_readers
import nidaqmx.stream_writers
import numpy as np  # For numerical operations
import math  # For mathematical operations

from nptdms import TdmsWriter, ChannelObject, RootObject, GroupObject

from nidaqmx.constants import FilterType, AcquisitionType, LoggingMode, LoggingOperation, READ_ALL_AVAILABLE

# Constants for DAQ configuration
FS_ACQ = 1000  # Sampling rate in Hz
FS_DISP = 10
SAMPLE_PER_BUFFER = int(FS_ACQ // FS_DISP)  # Number of samples to read per channel
print(FS_ACQ, FS_DISP, SAMPLE_PER_BUFFER)

CHANNELS = ["Dev2/ai0", "Dev2/ai1", "Dev2/ai2", "Dev2/ai3"]  # List of analog input channels
CHANNEL_NAMES = ["USD1", "USD2", "USD3", "USD4"]
GROUP_NAME = "DAQ_DATA_TEST"
FILE_NAME = "daq_data.tdms"  # File name for logging data

CH_OBJ_LIST = []
GROUP_OBJ = GroupObject(GROUP_NAME)
ROOT_OBJ = RootObject(properties={"description": "NIDAQmx Acquisition"})

# Create a global task object for the DAQ
analog_task = nidaqmx.Task()
input_reader = nidaqmx.stream_readers.AnalogMultiChannelReader(analog_task.in_stream)

sensor_in_buffer = np.zeros((len(CHANNELS), SAMPLE_PER_BUFFER), dtype=np.float32)
filter_out = np.zeros((len(CHANNELS), SAMPLE_PER_BUFFER), dtype=np.float32)


tdms_file = open(FILE_NAME, 'wb')
tdms_writer = TdmsWriter(tdms_file)

def low_pass_filter(data, window_size=5):
    kernel = np.ones(window_size) / window_size
    return np.convolve(data, kernel, mode='same')

def read_ai_task_callback(task_idx, event_type, num_samples, callback_data=None):
    buffer = np.zeros((len(CHANNELS), SAMPLE_PER_BUFFER))
    input_reader.read_many_sample(buffer, SAMPLE_PER_BUFFER, timeout=nidaqmx.constants.WAIT_INFINITELY)
 
    list = []
    for i in range(len(CHANNEL_NAMES)):
        filter_out[i,:] = low_pass_filter(buffer[i,:])
        list.append(ChannelObject(GROUP_NAME, CHANNEL_NAMES[i], filter_out[i,:]))
    tdms_writer.write_segment(list)

    return 0

def setup_tasks():
    # Set up the first analog input channel
    for c in CHANNELS:
        analog_task.ai_channels.add_ai_voltage_chan(c)

    # Configure the sampling clock timing for continuous acquisition
    analog_task.timing.cfg_samp_clk_timing(
        rate=FS_ACQ,  # Sampling rate in Hz
        sample_mode=AcquisitionType.CONTINUOUS,  # Continuous sampling mode
        samps_per_chan=SAMPLE_PER_BUFFER  # Number of samples per channel
    )

    # # Configure logging to save data to a TDMS file
    # analog_task.in_stream.configure_logging(
    #     file_path=FILE_NAME,  # Path to the TDMS file
    #     logging_mode=LoggingMode.LOG_AND_READ,  # Log data and allow reading
    #     operation=LoggingOperation.CREATE_OR_REPLACE  # Create or overwrite the file
    # )

    analog_task.register_every_n_samples_acquired_into_buffer_event(50, read_ai_task_callback)

def setup_tdms():
    tdms_data = [ROOT_OBJ, GROUP_OBJ]
    for i in range(len(CHANNEL_NAMES)):
        tdms_data.append(ChannelObject(group=GROUP_NAME, channel=CHANNEL_NAMES[i], data=np.array([])))

    print(tdms_data)

    tdms_writer.write_segment(tdms_data)

def main():
    
    setup_tasks()
    setup_tdms()

    print("Starting data collection. Press Ctrl+C to stop.")
    analog_task.start()

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
        analog_task.stop()  # Stop the DAQ task
        tdms_writer.close()
        tdms_file.close()