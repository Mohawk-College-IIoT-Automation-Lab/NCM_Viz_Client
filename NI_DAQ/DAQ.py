import nidaqmx  # Library for interfacing with NI DAQ (Data Acquisition) devices
import nidaqmx.constants  # Contains configuration enums like AcquisitionType, FilterType, etc.
import nidaqmx.stream_readers  # For efficient reading of continuous data streams
import numpy as np  # For efficient numerical operations and array handling'
from scipy.signal import butter, filtfilt, medfilt  # For filtering operations

from nptdms import TdmsWriter, ChannelObject, RootObject, GroupObject  # For TDMS file structure and writing

import json
from pydantic import BaseModel
from typing import List

import asyncio
from multiprocessing import Event

from .GenericMqtteLogger.logger import Logger
from .GenericMqtteLogger.generic_mqtt import GenericMQTT  # For MQTT communication

class SensorReadings(BaseModel):
    LL: float
    LQ: float
    RR: float
    RQ: float
    
class SensorData(BaseModel):
    Ultra_Sonic_Distance: SensorReadings
    Anemometer: SensorReadings

class DAQConfig(BaseModel):
    device_name: str = "Dev2"
    channels: List[str] = ["Dev2/ai0", "Dev2/ai1", "Dev2/ai2", "Dev2/ai3"]
    channel_names: List[str] = ["USD1", "USD2", "USD3", "USD4"]
    file_name: str = "default.tdms"
    fs: int = 2000
    fs_disp: int = 15
    filter_config: int = 1
    lpf_cutoff: float = 500.0
    hpf_cutoff: float = 0.01
    butter_order: int = 5
    host_name: str = "localhost"
    host_port: int = 1883

class DAQ(GenericMQTT):

    _running = False
    _instance = None

    @classmethod
    def get_instance(cls, config: DAQConfig):
        if cls._instance is None:
            cls._instance = cls(config, Logger("DAQ"))
        return cls._instance

    def __init__(self, config: DAQConfig, logger: Logger = None):

        if getattr(self, '_initialized', False):
            return
        
        self._initialized = True
    
        self._config = config
        self._device_name = config.device_name
        self._channels = config.channels
        self._channel_names = config.channel_names
        self._file_name = config.file_name
        self._fs = config.fs
        self._fs_disp = config.fs_disp
        self._filter_config = config.filter_config
        self._lpf_cutoff = config.lpf_cutoff
        self._hpf_cutoff = config.hpf_cutoff
        self._butter_order = config.butter_order

        super().__init__(self._config.host_name, self._config.host_port, logger)
        self.logger.debug("[DAQ] Initializing DAQ...")

        # Calculate the sample rate and buffer sizes
        self._fs_sample = self._fs * 2
        self._buffer_size = int(self._fs_sample / self._fs_disp) + 1
        self.logger.debug(f"[DAQ][init] Fs: {self._fs}, Fs Sample: {self._fs_sample}, Fs Disp: {self._fs_disp}, Buffer Size: {self._buffer_size}")

        # Calculate the filter parameters
        self._low = self._lpf_cutoff / self._fs
        self._high = self._hpf_cutoff / self._fs
        self._filt_params = [self._low, self._high]
        self.logger.debug(f"[DAQ][init] Low: {self._lpf_cutoff} : {self._low}, High: {self._hpf_cutoff} : {self._high}")
        self.logger.debug(f"[DAQ][init] Filter Config: {self._filter_config}")

        # Place holders for the filter coefficients
        self._a = None
        self._b = None

        # Setup filters
        self._setup_filter()

        # Used by the TDMS file
        self._group_obj = GroupObject("NCM")  # TDMS group that holds related channels
        self._raw_group_obj = GroupObject("Raw")  # TDMS group for raw data
        self._filter_group_obj = GroupObject("Filtered")  # TDMS group for filtered data
        self._root_obj = RootObject(properties={"description": "NIDAQmx Acquisition"})  # TDMS root metadata

        # Place holders for the tdms file and writer
        self._tdms_file = None
        self._tdms_writer = None

        # Setup Ni-daqmx task   
        self._task = nidaqmx.Task()  # Main acquisition task
        self._input_reader = nidaqmx.stream_readers.AnalogMultiChannelReader(self._task.in_stream)  # Efficient streaming reader

        # Condigure the ni-daqmx task and add channels
        for c in self._channels:
            self._task.ai_channels.add_ai_voltage_chan(c)
        self._task.timing.cfg_samp_clk_timing(self._fs_sample, sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS, samps_per_chan=self._buffer_size)
        self._task.register_every_n_samples_acquired_into_buffer_event(self._buffer_size, self._raw_data_callback)

        # setup buffers for raw and filtered data
        self._raw_data_buffer = np.zeros((len(self._channels), self._buffer_size), dtype=np.float32)
        self._filter_data_buffer = np.zeros((len(self._channels), self._buffer_size), dtype=np.float32)

        self.logger.debug(f"[DAQ][init] Connecting to MQTT")
        self.mqtt_connect()

        self.mqtt_client.message_callback_add("NCM/Experiment/Start", self._mqtt_start_callback)
        self.mqtt_client.message_callback_add("NCM/Experiment/Stop", self._mqtt_stop_callback)
        self.mqtt_client.message_callback_add("NCM/Experiment/Rename", self._mqtt_rename_callback)

    def _mqtt_start_callback(self, client, userdata, message):
        self.logger.debug(f"[MQTT] Start recording command received")
        if not self.is_recording:
            self.start_recording()
        else:
            self.logger.debug("[DAQ] DAQ task is already running.")

    def _mqtt_stop_callback(self, client, userdata, message):
        self.logger.debug(f"[MQTT] Stop recording command received")
        if self.is_recording:
            self.stop_recording()
        else:
            self.logger.debug("[DAQ] DAQ task is not running.")

    def _mqtt_rename_callback(self, client, userdata, message):
        self.logger.debug(f"[MQTT] Rename command received, data received: {message.payload.decode()}")
        data = json.loads(message.payload.decode())
        file_name = data.get("file_name", None)
        if file_name is not None:
            self.rename_file(file_name)
        else:
            self.logger.error("[DAQ] File name is None. Cannot rename TDMS file.")
            Exception("File name is None. Cannot rename TDMS file.")

    def _raw_data_callback(self, task_idx, event_type, num_samples, callback_data=None):
        # Get Data
        self._input_reader.read_many_sample(self._raw_data_buffer, self._buffer_size, timeout=nidaqmx.constants.WAIT_INFINITELY)

        # Filter
        self._filter_data_buffer = self._filter_data(self._raw_data_buffer)

        # Write to TDMS in a coroutine
        asyncio.create_task(self._write_tdms(self._raw_data_buffer, self._filter_data_buffer))

        # Calculate display avg
        avg = np.mean(self._filter_data_buffer, axis=0)

        # Create SensorData object
        sensor_data = SensorData(
            Ultra_Sonic_Distance=SensorReadings(LL=avg[0], LQ=avg[1], RQ=avg[2], RR=avg[3]),
            Anemometer=SensorReadings(LL=avg[4], LQ=avg[5], RQ=avg[6], RR=avg[7])
        )
        
        # push to mqtt
        asyncio.create_task(self.mqtt_client.publish("NCM/DisplayData", sensor_data.model_dump_json()))

    def _new_tdms(self, file_name: str):
        self.logger.debug(f"[DAQ] Trying to cerate TDMS file {self._file_name}")
        try:
            self._file_name = file_name
            self._tdms_file = open(self._file_name, 'wb')
            self._tdms_writer = TdmsWriter(self._tdms_file)
            self._tdms_writer.write_segment([self._root_obj, self._group_obj])
            self.logger.debug(f"[DAQ] Created new TDMS file: {file_name}")
        except Exception as e:
            self.logger.error(f"[DAQ] Exception when closing TDMS {self._file_name}: {e}")


    def _close_tdms(self):
        # Close the TDMS file
        self.logger.debug(f"[DAQ] Trying to close TDMS file: {self._file_name}")
        try:
            self._tdms_writer.close()
            self._tdms_file.close()
            self.logger.debug(f"[DAQ] TDMS file closed: {self._file_name}")
        except Exception as e:
            self.logger.error(f"[DAQ] Exception when closing TDMS {self._file_name}: {e}")

    def close(self):
        # Close the DAQ task
        self.logger.debug("[DAQ] Closing DAQ task...")
        self._task.close()
        
        self.logger.debug("[DAQ] Disconnecting from MQTT...")
        self.mqtt_disconnect()

        self.logger.debug("[DAQ] Closing TDMS file...")
        self._close_tdms()

    def start_recording(self):
        if self._task.is_task_done():
            self.logger.debug("[DAQ] Starting DAQ task and creating TDMS")
            self._new_tdms(self._config.file_name)
            self._task.start()
        else:
            self.logger.debug("[DAQ] DAQ task is already running.")

    def stop_recording(self):
        self.logger.debug("[DAQ] Stopping DAQ task...")
        self._task.stop()
        self._close_tdms()

    def rename_file(self, file_name: str):
        self.logger.debug(f"[DAQ] Renaming TDMS file to: {file_name}")
        if file_name is None:
            self.logger.error("[DAQ] File name is None. Cannot rename TDMS file.")
            raise ValueError("File name is None. Cannot rename TDMS file.")
        elif not self.is_recording:
            self.logger.error("[DAQ] Cannot rename TDMS while recording.")
            raise Exception("Cannot rename TDMS while recording.")
        else:
            self._close_tdms()
            if ".log" not in file_name:
                file_name += ".log"
            self._file_name = file_name
            self._new_tdms(self._file_name)

    async def publish(self, topic: str, payload: str):
        if self.connected:
            self.mqtt_client.publish(topic, payload)
            self.logger.debug(f"[MQTT] Publishing to topic: {topic} with payload: {payload}")

    @property
    def is_recording(self):
        return not self._task.is_task_done()

    async def _write_tdms(self, raw:np.ndarray, filtered:np.ndarray):
        # Create a TDMS-compatible list of ChannelObjects with filtered data
        try:
            channel_objects = []

            for i in range(len(self._channel_names)):
                channel_objects.append(ChannelObject(self._raw_group_obj, self._channel_names[i], raw[i, :]))
                channel_objects.append(ChannelObject(self._filter_group_obj, self._channel_names[i], filtered[i, :]))
            
            self._tdms_writer.write_segment(channel_objects)
        except Exception as e:
            self.logger.error(f"[DAQ] TDMS Writing exceptions : {e}")

    def _setup_filter(self):
        self.logger.debug(f"[DAQ] Setting up filter with config: {self._filter_config}")
        if self._filter_config == 0:
            # No filter
            self._a = None
            self._b = None
        elif self._filter_config == 1:
            # Low-pass filter
            self._create_lowpass_filter()
        elif self._filter_config == 2:
            # High-pass filter
            self._create_highpass_filter()
        elif self._filter_config == 3:
            # Band-pass filter
            self._create_bandpass_filter()
        else:
            self.logger.error(f"[DAQ] Invalid filter configuration: {self._filter_config}")
            raise ValueError(f"Invalid filter configuration : {self._filter_config}")
        
    def _filter_data(self, data: np.ndarray):
        if self._a is not None and self._b is not None:
            # Apply the filter to the data
            filtered_data = filtfilt(self._b, self._a, data)
            return filtered_data
        else:
            return data
        
    def _create_bandpass_filter(self):
        b, a = butter(self._butter_order, self._filt_params, btype='band')
        self._a = a
        self._b = b
        self.logger.debug(f"[DAQ] Bandpass filter created with params: {self._filt_params}")

    def _create_lowpass_filter(self):
        b, a = butter(self._butter_order, self._low, btype='low')
        self._a = a
        self._b = b
        self.logger.debug(f"[DAQ] Lowpass filter created with params: {self._low}")

    def _create_highpass_filter(self):
        b, a = butter(self._butter_order, self._high, btype='high')
        self._a = a
        self._b = b
        self.logger.debug(f"[DAQ] Highpass filter created with params: {self._high}")

    @classmethod
    def stop(cls, stop_event:Event): # type: ignore
        stop_event.set()
        print("stop")

    @classmethod
    def run(cls, daq_config : DAQConfig, stop_event:Event): # type: ignore

        daq = DAQ.get_instance(daq_config)

        while not stop_event.is_set():
            daq.mqtt_client.loop(0.01)

        print("stopping")
        daq.close()