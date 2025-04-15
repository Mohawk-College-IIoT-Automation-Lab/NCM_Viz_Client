# --- Imports ---
import nidaqmx  # Library for interfacing with NI DAQ (Data Acquisition) devices
import time  # Used to pause execution and keep the main loop running
import nidaqmx.constants  # Contains configuration enums like AcquisitionType, FilterType, etc.
import nidaqmx.stream_readers  # For efficient reading of continuous data streams
import numpy as np  # For efficient numerical operations and array handling

from nptdms import TdmsWriter, ChannelObject, RootObject, GroupObject  # For TDMS file structure and writing

FS_ACQ = 1000  # Acquisition sampling frequency in Hz
FS_DISP = 10  # Display frequency (used for buffer size)
SAMPLE_PER_BUFFER = int(FS_ACQ // FS_DISP)  # Number of samples to read per callback
print(FS_ACQ, FS_DISP, SAMPLE_PER_BUFFER)  # Debug: confirm sampling setup

# Define which channels to read from and how to label them in TDMS
CHANNELS = ["Dev2/ai0", "Dev2/ai1", "Dev2/ai2", "Dev2/ai3"]  # DAQ device/port/channel
CHANNEL_NAMES = ["USD1", "USD2", "USD3", "USD4"]  # Friendly names for TDMS channels
GROUP_NAME = "DAQ_DATA_TEST"  # Group name inside the TDMS file
FILE_NAME = "daq_data.tdms"  # Name of the output file

# --- TDMS Objects Setup ---
CH_OBJ_LIST = []  # Not used, can likely be removed
GROUP_OBJ = GroupObject(GROUP_NAME)  # TDMS group that holds related channels
ROOT_OBJ = RootObject(properties={"description": "NIDAQmx Acquisition"})  # TDMS root metadata

# --- NI-DAQmx Task Setup ---
analog_task = nidaqmx.Task()  # Main acquisition task
input_reader = nidaqmx.stream_readers.AnalogMultiChannelReader(analog_task.in_stream)  # Efficient streaming reader

# Buffers for raw input and filtered output
sensor_in_buffer = np.zeros((len(CHANNELS), SAMPLE_PER_BUFFER), dtype=np.float32)
filter_out = np.zeros((len(CHANNELS), SAMPLE_PER_BUFFER), dtype=np.float32)

# TDMS file writer
tdms_file = open(FILE_NAME, 'wb')  # Open the file manually
tdms_writer = TdmsWriter(tdms_file)  # Create the TDMS writer object

# --- Low-pass filter implementation ---
def low_pass_filter(data, window_size=5):
    # Simple moving average filter
    kernel = np.ones(window_size) / window_size
    return np.convolve(data, kernel, mode='same')  # Apply filtering across the data array

# --- Callback function triggered by the DAQ on each buffer fill ---
def read_ai_task_callback(task_idx, event_type, num_samples, callback_data=None):
    # Create a temporary buffer to hold new data
    buffer = np.zeros((len(CHANNELS), SAMPLE_PER_BUFFER))
    
    # Read new samples into the buffer
    input_reader.read_many_sample(buffer, SAMPLE_PER_BUFFER, timeout=nidaqmx.constants.WAIT_INFINITELY)

    # Create a TDMS-compatible list of ChannelObjects with filtered data
    list = []
    for i in range(len(CHANNEL_NAMES)):
        filter_out[i, :] = low_pass_filter(buffer[i, :])  # Apply filter per channel
        list.append(ChannelObject(GROUP_NAME, CHANNEL_NAMES[i], filter_out[i, :]))  # Build TDMS channel data

    # Write filtered data segment to the TDMS file
    tdms_writer.write_segment(list)

    return 0  # Required: return 0 from callback (int type) to avoid ctypes errors

# --- Setup the NI-DAQmx task ---
def setup_tasks():
    # Add all input voltage channels to the task
    for c in CHANNELS:
        analog_task.ai_channels.add_ai_voltage_chan(c)

    # Set timing for continuous acquisition
    analog_task.timing.cfg_samp_clk_timing(
        rate=FS_ACQ,  # Sampling frequency
        sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS,  # Continuous streaming mode
        samps_per_chan=SAMPLE_PER_BUFFER  # Number of samples to acquire per buffer
    )

    # Register the callback to be triggered every SAMPLE_PER_BUFFER samples
    analog_task.register_every_n_samples_acquired_into_buffer_event(
        SAMPLE_PER_BUFFER, read_ai_task_callback
    )

# --- Write the initial TDMS structure before logging data ---
def setup_tdms():
    tdms_data = [ROOT_OBJ, GROUP_OBJ]  # TDMS requires root and group metadata

    # Add empty ChannelObjects to define structure in TDMS
    for i in range(len(CHANNEL_NAMES)):
        tdms_data.append(ChannelObject(group=GROUP_NAME, channel=CHANNEL_NAMES[i], data=np.array([])))

    tdms_writer.write_segment(tdms_data)  # Write the initial segment

# --- Main function ---
def main():
    setup_tasks()  # Configure DAQ hardware
    setup_tdms()   # Set up TDMS file layout

    print("Starting data collection. Press Ctrl+C to stop.")
    analog_task.start()  # Start acquisition

# --- Run only if this script is the main one executed ---
if __name__ == "__main__":
    main()
    try:
        # Keep the script running so the DAQ can keep acquiring
        while True:
            time.sleep(1)  # Sleep to prevent CPU overload
    except KeyboardInterrupt:
        # Gracefully stop everything on Ctrl+C
        print("Exiting...")
        analog_task.stop()         # Stop the task
        tdms_writer.close()        # Close the TDMS writer
        tdms_file.close()          # Close the file
