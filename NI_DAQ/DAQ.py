import nidaqmx  # Library for interfacing with NI DAQ (Data Acquisition) devices
import nidaqmx.constants  # Contains configuration enums like AcquisitionType, FilterType, etc.
import nidaqmx.stream_readers  # For efficient reading of continuous data streams
import numpy as np  # For efficient numerical operations and array handling'
from scipy.signal import butter, filtfilt, medfilt  # For filtering operations

from nptdms import TdmsWriter, ChannelObject, RootObject, GroupObject  # For TDMS file structure and writing

import json
from pydantic import BaseModel
from typing import List
import logging

import asyncio
from multiprocessing import Event

from Constants.base_models import SensorData, SensorReadings
from Constants.configs import DAQConfig, FilterConfig, LowPassConfig, HighPassConfig, BandPassConfig
from .GenericMqtteLogger.davids_logger import initialize_logging
from .GenericMqtteLogger.generic_mqtt import GenericMQTT  # For MQTT communication

class DAQ(GenericMQTT):

    _running = False
    _instance = None

    @classmethod
    def get_instance(cls, config: DAQConfig = DAQConfig):
        if cls._instance is None:
            cls._instance = cls(config)
        return cls._instance

    def __init__(self, config: DAQConfig):

        if getattr(self, '_initialized', False):
            return
        
        self._initialized = True
        self._config = config

        super().__init__(log_name=config.log_config.log_name, host_name=config.mqtt_config.host_name, host_port=config.mqtt_config.host_port)
        logging.debug("[DAQ] Initializing DAQ...")

        # Calculate the sample rate and buffer sizes
        self._fs_sample = config.fs * 2
        self._buffer_size = int(self._fs_sample / config.fs_disp) + 1
        logging.debug(f"[DAQ][init] Fs: {config.fs}, Fs Sample: {self._fs_sample}, Fs Disp: {config.fs_disp}, Buffer Size: {self._buffer_size}")

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
        self._file_name = config.file_name
        self._tdms_file = None
        self._tdms_writer = None

        # Setup Ni-daqmx task   
        self._task = nidaqmx.Task()  # Main acquisition task
        self._input_reader = nidaqmx.stream_readers.AnalogMultiChannelReader(self._task.in_stream)  # Efficient streaming reader

        # Condigure the ni-daqmx task and add channels
        for c in config.channels:
            self._task.ai_channels.add_ai_voltage_chan(c)
        self._task.timing.cfg_samp_clk_timing(self._fs_sample, sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS, samps_per_chan=self._buffer_size)
        self._task.register_every_n_samples_acquired_into_buffer_event(self._buffer_size, self._raw_data_callback)

        # setup buffers for raw and filtered data
        self._raw_data_buffer = np.zeros((len(config.channels), self._buffer_size), dtype=np.float32)
        self._filter_data_buffer = np.zeros((len(config.channels), self._buffer_size), dtype=np.float32)

        logging.debug(f"[DAQ][init] Connecting to MQTT")
        self.mqtt_connect()

        self.mqtt_client.message_callback_add("NCM/Experiment/Start", self._mqtt_start_callback)
        self.mqtt_client.message_callback_add("NCM/Experiment/Stop", self._mqtt_stop_callback)
        self.mqtt_client.message_callback_add("NCM/Experiment/Rename", self._mqtt_rename_callback)

    def _mqtt_start_callback(self, client, userdata, message):
        logging.debug(f"[MQTT] Start recording command received")
        if not self.is_recording:
            self.start_recording()
        else:
            logging.debug("[DAQ] DAQ task is already running.")

    def _mqtt_stop_callback(self, client, userdata, message):
        logging.debug(f"[MQTT] Stop recording command received")
        if self.is_recording:
            self.stop_recording()
        else:
            logging.debug("[DAQ] DAQ task is not running.")

    def _mqtt_rename_callback(self, client, userdata, message):
        logging.debug(f"[MQTT] Rename command received, data received: {message.payload.decode()}")
        data = json.loads(message.payload.decode())
        file_name = data.get("file_name", None)
        if file_name is not None:
            self.stop_recording()
            self._new_tdms(file_name)
        else:
            logging.error("[DAQ] File name is None. Cannot rename TDMS file.")
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
        logging.debug(f"[DAQ] Trying to cerate TDMS file {self._file_name}")
        try:
            self._file_name = file_name
            self._tdms_file = open(self._file_name, 'wb')
            self._tdms_writer = TdmsWriter(self._tdms_file)
            self._tdms_writer.write_segment([self._root_obj, self._group_obj])
            logging.debug(f"[DAQ] Created new TDMS file: {file_name}")
        except Exception as e:
            logging.error(f"[DAQ] Exception when closing TDMS {self._file_name}: {e}")


    def _close_tdms(self):
        # Close the TDMS file
        logging.debug(f"[DAQ] Trying to close TDMS file: {self._file_name}")
        try:
            self._tdms_writer.close()
            self._tdms_file.close()
            logging.debug(f"[DAQ] TDMS file closed: {self._file_name}")
        except Exception as e:
            logging.error(f"[DAQ] Exception when closing TDMS {self._file_name}: {e}")

    def _start_recording(self, filename:str="default"):
        if self._task.is_task_done():
            logging.debug("[DAQ] Starting DAQ task and creating TDMS")
            self._new_tdms(self._config.file_name)
            self._task.start()
        else:
            logging.debug("[DAQ] DAQ task is already running.")

    def _stop_recording(self):
        logging.debug("[DAQ] Stopping DAQ task...")
        self._task.stop()
        self._close_tdms()

    async def publish(self, topic: str, payload: str):
        if self.connected:
            self.mqtt_client.publish(topic, payload)
            logging.debug(f"[MQTT] Publishing to topic: {topic} with payload: {payload}")

    @property
    def is_recording(self):
        return not self._task.is_task_done()

    async def _write_tdms(self, raw:np.ndarray, filtered:np.ndarray):
        # Create a TDMS-compatible list of ChannelObjects with filtered data
        try:
            channel_objects = []

            for i in range(len(self._channel_names)):
                channel_objects.append(ChannelObject(self._raw_group_obj, self._config.channel_names[i], raw[i, :]))
                channel_objects.append(ChannelObject(self._filter_group_obj, self._config.channel_names[i], filtered[i, :]))
            
            self._tdms_writer.write_segment(channel_objects)
        except Exception as e:
            logging.error(f"[DAQ] TDMS Writing exceptions : {e}")

    def _setup_filter(self):
        logging.debug(f"[DAQ] Setting up filter with config: {self._config.filter_config.type}")
        low = self._config.filter_config.lpf_cutoff / self._config.fs
        high = self._config.filter_config.hpf_cutoff / self._config.fs

        if self._config.filter_config.__class__ == FilterConfig:
            # No filter
            self._a = None
            self._b = None
            low = 0
            high = 0

        elif self._config.filter_config.__class__ == BandPassConfig:
            b, a = butter(self._config.filter_config.order, [high, low], btype='bandpass') 

        elif self._config.filter_config.__class__ == LowPassConfig:
            b, a = butter(self._config.filter_config.order, [low], btype='lowpass') 

        elif self._config.filter_config.__class__ == BandPassConfig:
            b, a = butter(self._config.filter_config.order, [high], btype='highpass') 
    
        self._a = a
        self._b = b
        logging.debug(f"[DAQ][init] Low: {self._config.filter_config.lpf_cutoff} : {low}, High: {self._config.filter_config.hpf_cutoff} : {high} created")
        
    def _filter_data(self, data: np.ndarray):
        if self._a is not None and self._b is not None:
            # Apply the filter to the data
            filtered_data = filtfilt(self._b, self._a, data)
            return filtered_data
        else:
            return data

    @classmethod
    def stop(cls, stop_event:Event): # type: ignore
        stop_event.set()
        print("stop")

    def close(self):
        # Close the DAQ task
        logging.debug("[DAQ] Closing DAQ task...")
        self._task.close()
        
        logging.debug("[DAQ] Disconnecting from MQTT...")
        self.mqtt_disconnect()

        logging.debug("[DAQ] Closing TDMS file...")
        self._close_tdms()

    @classmethod
    def run(cls, daq_config : DAQConfig, stop_event:Event): # type: ignore

        daq = DAQ.get_instance(daq_config)

        while not stop_event.is_set():
            daq.mqtt_client.loop(0.01)

        print("stopping")
        daq.close()