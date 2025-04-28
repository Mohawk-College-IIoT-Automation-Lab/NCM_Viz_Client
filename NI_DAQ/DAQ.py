import nidaqmx  # Library for interfacing with NI DAQ (Data Acquisition) devices
import nidaqmx.constants  # Contains configuration enums like AcquisitionType, FilterType, etc.
import nidaqmx.stream_readers  # For efficient reading of continuous data streams
import numpy as np  # For efficient numerical operations and array handling'
from scipy.signal import butter, filtfilt, medfilt  # For filtering operations

from nptdms import TdmsWriter, ChannelObject, RootObject, GroupObject  # For TDMS file structure and writing

import json
from pydantic import BaseModel

class SensorReadings(BaseModel):
    LL: float
    LQ: float
    RR: float
    RQ: float
    
class SensorData(BaseModel):
    Ultra_Sonic_Distance: SensorReadings
    Anemometer: SensorReadings

class DAQ_Config(BaseModel):
    device_name: str = "Dev2"
    channels: list[str] = ["Dev2/ai0", "Dev2/ai1", "Dev2/ai2", "Dev2/ai3"]
    channel_names: list[str] = ["USD1", "USD2", "USD3", "USD4"]
    file_name: str = "default.tdms"
    fs: int = 2000
    fs_disp: int = 15
    output_freq: int = 1
    filter_config: int = 0 # no filt, lpf, hpf, bandpass
    lpf_cutoff: float = 500
    hpf_cutoff: float = 0.01
    butter_order: int = 5

class DAQ_Factory:
    _instance = None

    @classmethod
    def get_instance(cls, config_value=None):
        if cls._instance is None:
            if config_value is None:
                raise ValueError("First time initialization requires config_value")
            cls._instance = DAQ(json=config_value)
        return cls._instance

class DAQ:
    def __init__(self, config: DAQ_Config):
        self._config = config

        self._device_name = self._config.device_name
        self._channels = self._config.channels
        self._channel_names = self._config.channel_names
        self._fs = self._config.fs
        self._fs_disp = self._config.fs_disp
        self._output_freq = self._config.output_freq
        self._lpf_cutoff = self._config.lpf_cutoff
        self._hpf_cutoff = self._config.hpf_cutoff
        self._butter_order = self._config.butter_order

        self._fs_sample = self._fs * 2

        self._low = self._lpf_cutoff / self._fs
        self._high = self._hpf_cutoff / self._fs
        self._filt_params = [self._low, self._high]

        self._filter_config = self._config.filter_config

        self._a = None
        self._b = None

        self._base_group_name = "NCM"
        self._raw_group_name = "Raw"
        self._lpf_group_name = "LPF"
        self._hpf_group_name = "HPF"

        self._group_obj = GroupObject(self._base_group_name)  # TDMS group that holds related channels
        self._root_obj = RootObject(properties={"description": "NIDAQmx Acquisition"})  # TDMS root metadata

        # Create TDMS file writer object
        self._tdms_file = open(self._file_name, 'wb')
        self._tdms_writer = TdmsWriter(self._tdms_file)
        self._tdms_writer.write_segment([self._root_obj, self._group_obj])  # Write the initial segment

        self._setup_filter()

    def _raw_data_callback(self, task_idx, event_type, num_samples, callback_data=None):

        pass

    def _display_data_callback(self, task_idx, event_type, num_samples, callback_data=None):

        pass
    
    def _setup_filter(self):
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
            raise ValueError("Invalid filter configuration")
        
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

    def _create_lowpass_filter(self):
        b, a = butter(self._butter_order, self._low, btype='low')
        self._a = a
        self._b = b

    def _create_highpass_filter(self):
        b, a = butter(self._butter_order, self._high, btype='high')
        self._a = a
        self._b = b

    def _close_tdms(self):
        # Close the TDMS file
        self._tdms_writer.close()
        self._tdms_file.close()

    def _close_task(self):
        # Close the DAQ task
        self._analog_task.close()