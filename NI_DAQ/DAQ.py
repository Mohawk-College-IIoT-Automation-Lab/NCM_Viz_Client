import nidaqmx  # Library for interfacing with NI DAQ (Data Acquisition) devices
from nidaqmx.scale import Scale
import nidaqmx.constants  # Contains configuration enums like AcquisitionType, FilterType, etc.
from nidaqmx.constants import VoltageUnits, TerminalConfiguration
import nidaqmx.stream_readers  # For efficient reading of continuous data streams
import numpy as np  # For efficient numerical operations and array handling'
from scipy.signal import  filtfilt, medfilt, butter  # For filtering operations

from nptdms import (
    TdmsWriter,
    ChannelObject,
    RootObject,
    GroupObject,
)  # For TDMS file structure and writing

import json
import logging
import time

from multiprocessing import Event

from Constants.base_models import SensorData, SensorReadings, StandingWave
from Constants.configs import (
    DAQConfig,
    ExperimentMqttConfig,
    LoggerConfig,
    SensorsConfig,
)
from .GenericMqtteLogger.davids_logger import initialize_logging
from .GenericMqtteLogger.generic_mqtt import (
    GenericMQTT,
)  # For MQTT communication


class DAQ(GenericMQTT):

    _running = False
    _instance = None

    @classmethod
    def get_instance(cls, logger_config: LoggerConfig):
        if cls._instance is None:
            cls._instance = cls(logger_config)
        return cls._instance

    def __init__(self, logger_config: LoggerConfig):
        if getattr(self, "_initialized", False):
            return

        self._initialized = True

        super().__init__(
            client_name="DAQMQTT",
            log_name=logger_config.log_name,
            host_name=logger_config.mqtt_config.host_name,
            host_port=logger_config.mqtt_config.host_port,
        )
        logging.debug("[DAQ] Initializing DAQ...")

        # Calculate the sample rate and buffer sizes
        self._buffer_size = int(DAQConfig.fs / DAQConfig.fs_disp)
        self._f_filt_nyq = DAQConfig.fs / 2
        self._f_lpf_norm = DAQConfig.lpf_cutoff / self._f_filt_nyq 



        logging.debug(
            f"[DAQ][init] Fs: {DAQConfig.fs}, Fs Disp: {DAQConfig.fs_disp}, Buffer Size: {self._buffer_size}"
        )
        logging.debug(
            f"[DAQ][init] Fnyq: {self._f_filt_nyq}, LPF_cutoff {DAQConfig.lpf_cutoff}, LPF_Order {DAQConfig.lpf_order}, LPF_Norm {self._f_lpf_norm}" 
        )   

        # filter Constants
        self._b, self._a = butter(DAQConfig.lpf_order, self._f_lpf_norm, btype='lowpass')
        
        

        # Used by the TDMS file
        self._group_obj = GroupObject("NCM")  # TDMS group that holds related channels
        self._raw_group_obj = GroupObject(
            "Raw"
        )  # TDMS group that holds related channels
        self._filt_group_obj = GroupObject(
            "Filtered"
        )  # TDMS group that holds related channels
        self._root_obj = RootObject(
            properties={"description": "NIDAQmx Acquisition"}
        )  # TDMS root metadata

        # Place holders for the tdms file and writer
        self._file_name = DAQConfig.file_name
        self._tdms_file = None
        self._tdms_writer = None

        # Setup Ni-daqmx task
        self._task = nidaqmx.Task()  # Main acquisition task
        self._input_reader = nidaqmx.stream_readers.AnalogMultiChannelReader(
            self._task.in_stream
        )  # Efficient streaming reader

        # Condigure the ni-daqmx task and add channels
        try:
            ultra_sonic_scale = Scale.create_map_scale(
                scale_name="ultrasonic",
                prescaled_min=DAQConfig.usd_pre_min,
                prescaled_max=DAQConfig.usd_pre_max,
                scaled_min=DAQConfig.usd_min,
                scaled_max=DAQConfig.usd_max,
                scaled_units="mm",
            )

            anemometer_scale = Scale.create_map_scale(
                scale_name="anemometer",
                prescaled_min=DAQConfig.anm_pre_min,
                prescaled_max=DAQConfig.anm_pre_max,
                scaled_min=DAQConfig.anm_min,
                scaled_max=DAQConfig.anm_max,
                scaled_units="mm",
            )

            self._task.ai_channels.add_ai_voltage_chan(
                physical_channel="cDAQ9185-2304EC6Mod3/ai0",
                name_to_assign_to_channel="USD-RR",
                terminal_config=TerminalConfiguration.DIFF,
                min_val=DAQConfig.usd_min,
                max_val=DAQConfig.usd_max,
                units=VoltageUnits.FROM_CUSTOM_SCALE,
                custom_scale_name="ultrasonic",
            )
            
            self._task.ai_channels.add_ai_voltage_chan(
                physical_channel="cDAQ9185-2304EC6Mod3/ai1",
                name_to_assign_to_channel="USD-RQ",
                terminal_config=TerminalConfiguration.DIFF,
                min_val=DAQConfig.usd_min,
                max_val=DAQConfig.usd_max,
                units=VoltageUnits.FROM_CUSTOM_SCALE,
                custom_scale_name="ultrasonic",
            )
           
            self._task.ai_channels.add_ai_voltage_chan(
                physical_channel="cDAQ9185-2304EC6Mod3/ai2",
                name_to_assign_to_channel="USD-LQ",
                terminal_config=TerminalConfiguration.DIFF,
                min_val=DAQConfig.usd_min,
                max_val=DAQConfig.usd_max,
                units=VoltageUnits.FROM_CUSTOM_SCALE,
                custom_scale_name="ultrasonic",
            )
            
            self._task.ai_channels.add_ai_voltage_chan(
                physical_channel="cDAQ9185-2304EC6Mod3/ai3",
                name_to_assign_to_channel="USD-LL",
                terminal_config=TerminalConfiguration.DIFF,
                min_val=DAQConfig.usd_min,
                max_val=DAQConfig.usd_max,
                units=VoltageUnits.FROM_CUSTOM_SCALE,
                custom_scale_name="ultrasonic",
            )
            
            self._task.ai_channels.add_ai_voltage_chan(
                physical_channel="cDAQ9185-2304EC6Mod3/ai4",
                name_to_assign_to_channel="ANM-RR",
                terminal_config=TerminalConfiguration.DIFF,
                min_val=DAQConfig.anm_min,
                max_val=DAQConfig.anm_max,
                units=VoltageUnits.FROM_CUSTOM_SCALE,
                custom_scale_name="anemometer",
            )
            
            self._task.ai_channels.add_ai_voltage_chan(
                physical_channel="cDAQ9185-2304EC6Mod3/ai5",
                name_to_assign_to_channel="ANM-RQ",
                terminal_config=TerminalConfiguration.DIFF,
                units=VoltageUnits.FROM_CUSTOM_SCALE,
                min_val=DAQConfig.anm_min,
                max_val=DAQConfig.anm_max,
                custom_scale_name="anemometer",
            )
            
            self._task.ai_channels.add_ai_voltage_chan(
                physical_channel="cDAQ9185-2304EC6Mod3/ai6",
                name_to_assign_to_channel="ANM-LQ",
                terminal_config=TerminalConfiguration.DIFF,
                min_val=DAQConfig.anm_min,
                max_val=DAQConfig.anm_max,
                units=VoltageUnits.FROM_CUSTOM_SCALE,
                custom_scale_name="anemometer",
            )

            self._task.ai_channels.add_ai_voltage_chan(
                physical_channel="cDAQ9185-2304EC6Mod3/ai7",
                name_to_assign_to_channel="ANM-LL",
                terminal_config=TerminalConfiguration.DIFF,
                min_val=DAQConfig.anm_min,
                max_val=DAQConfig.anm_max,
                units=VoltageUnits.FROM_CUSTOM_SCALE,
                custom_scale_name="anemometer",
            )
            
            self._task.timing.cfg_samp_clk_timing(
                DAQConfig.fs,
                sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS,
                samps_per_chan=self._buffer_size,
            )

            self._task.register_every_n_samples_acquired_into_buffer_event(
                self._buffer_size, self._raw_data_callback
            )
        except Exception as e:
            logging.error(f"[DAQ] DAQ setup exception: {e}")
            raise e

        # setup buffers for raw and filtered data
        self._raw_data_buffer = np.zeros(
            (len(DAQConfig.physical_names), self._buffer_size), dtype=np.float64
        )

        self._filter_data_buffer = np.zeros(
            (len(DAQConfig.physical_names), self._buffer_size), dtype=np.float64
        )

        self._start_timer = None

        logging.debug(f"[DAQ][MQTT][init] Connecting to MQTT")
        self.mqtt_client.on_connect = self._on_connect
        self.mqtt_connect()

    def _on_connect(self, client, userdata, flags, rc, pros=None):

        topic = f"{ExperimentMqttConfig.base_topic}{ExperimentMqttConfig.start_topic}"
        client.subscribe(topic)
        client.message_callback_add(topic, self._mqtt_start_callback)
        logging.debug(
            f"[DAQ][MQTT][init] Subbing and setting up callback for topic: {topic}"
        )

        topic = f"{ExperimentMqttConfig.base_topic}{ExperimentMqttConfig.stop_topic}"
        client.subscribe(topic)
        client.message_callback_add(topic, self._mqtt_stop_callback)
        logging.debug(
            f"[DAQ][MQTT][init] Subbing and setting up callback for topic: {topic}"
        )

        topic = f"{ExperimentMqttConfig.base_topic}{ExperimentMqttConfig.rename_topic}"
        client.subscribe(topic)
        client.message_callback_add(topic, self._mqtt_rename_callback)
        logging.debug(
            f"[DAQ][MQTT][init] Subbing and setting up callback for topic: {topic}"
        )

    def _mqtt_start_callback(self, client, userdata, msg):
        logging.debug(f"[DAQ][MQTT] Start recording command received")
        if not self.is_recording:
            self._start_recording()
        else:
            logging.debug("[DAQ][MQTT]  DAQ task is already running.")

    def _mqtt_stop_callback(self, client, userdata, msg):
        logging.debug(f"[DAQ][MQTT]  Stop recording command received")
        if self.is_recording:
            self._stop_recording()
        else:
            logging.debug("[DAQ][MQTT]  DAQ task is not running.")

    def _mqtt_rename_callback(self, client, userdata, msg):
        logging.debug(
            f"[DAQ][MQTT]  Rename command received, data received: {msg.payload.decode()}"
        )
        data = json.loads(msg.payload.decode())
        file_name = data.get("file_name", None)
        if file_name is not None:
            self._stop_recording()
            self._new_tdms(file_name)
        else:
            logging.error("[DAQ][MQTT]  File name is None. Cannot rename TDMS file.")
            Exception("File name is None. Cannot rename TDMS file.")

    def _raw_data_callback(self, task_idx, event_type, num_samples, callback_data=None):
        timer = time.time() - self._start_timer
        self.mqtt_client.publish(
            f"{ExperimentMqttConfig.base_topic}{ExperimentMqttConfig.elapsed_topic}",
            timer,
        )

        try:
            # Get Data

            self._input_reader.read_many_sample(
                self._raw_data_buffer, self._buffer_size
            )
            
            # kernel for median filter
            kernel = 21
            for i in range(0, len(DAQConfig.physical_names)):
                # Add offsets to sensors 
                # self._raw_data_buffer[i] = DAQConfig.usd_zero - (self._raw_data_buffer[i] + DAQConfig.offsets[i])
                self._raw_data_buffer[i] = self._raw_data_buffer[i] + DAQConfig.offsets[i]

                # Apply low pass filter
                self._filter_data_buffer[i] = filtfilt(self._b, self._a, self._raw_data_buffer[i])
                # Apply median filter
                self._filter_data_buffer[i] = medfilt(self._filter_data_buffer[i], kernel)
            
            # Write to TDMS in a coroutine
            self._write_tdms(self._raw_data_buffer, self._filter_data_buffer)

            # Calculate display avg
            RR_usd_avg = round(np.mean(self._filter_data_buffer[0]), DAQConfig.usd_sig_figs)
            RQ_usd_avg = round(np.mean(self._filter_data_buffer[1]), DAQConfig.usd_sig_figs)
            LQ_usd_avg = round(np.mean(self._filter_data_buffer[2]), DAQConfig.usd_sig_figs)
            LL_usd_avg = round(np.mean(self._filter_data_buffer[3]), DAQConfig.usd_sig_figs)
            RR_anm_avg = round(np.mean(self._filter_data_buffer[4]), DAQConfig.anm_sig_figs)
            RQ_anm_avg = round(np.mean(self._filter_data_buffer[5]), DAQConfig.anm_sig_figs)
            LQ_anm_avg = round(np.mean(self._filter_data_buffer[6]), DAQConfig.anm_sig_figs)
            LL_anm_avg = round(np.mean(self._filter_data_buffer[7]), DAQConfig.anm_sig_figs)

            # Create SensorData object
            sensor_data = SensorData(
                Ultra_Sonic_Distance=SensorReadings(
                    LL=LL_usd_avg, LQ=LQ_usd_avg, RQ=RQ_usd_avg, RR=RR_usd_avg
                ),
                Anemometer=SensorReadings(
                    LL=LL_anm_avg, LQ=LQ_anm_avg, RQ=RQ_anm_avg, RR=RR_anm_avg
                ),
                Standing_Wave=StandingWave(
                    Left=LL_usd_avg - LQ_usd_avg, Right=RR_usd_avg - RQ_usd_avg
                ),
            )

            # push to mqtt
            self.mqtt_client.publish(
                SensorsConfig.display_data_topic, sensor_data.model_dump_json()
            )

        except Exception as e:
            logging.error(f"[DAQ] Exception: {e}")

        return 0  # this is a must have apparently

    def _start_recording(self):
        if self._task.is_task_done():
            logging.debug("[DAQ] Starting DAQ task and creating TDMS")
            self._new_tdms(self._file_name)
            self._task.start()
            self._start_timer = time.time()
        else:
            logging.debug("[DAQ] DAQ task is already running.")

    def _stop_recording(self):
        logging.debug("[DAQ] Stopping DAQ task...")
        self._task.stop()
        self._close_tdms()

    @property
    def is_recording(self):
        return not self._task.is_task_done()

    def _new_tdms(self, file_name: str):
        logging.debug(f"[DAQ] Trying to cerate TDMS file {self._file_name}")
        try:
            self._file_name = file_name
            if not self._file_name.endswith(".tdms"):
                self._file_name += ".tdms"
            self._tdms_file = open(self._file_name, "wb")
            self._tdms_writer = TdmsWriter(self._tdms_file)
            self._tdms_writer.write_segment([self._root_obj, self._group_obj])
            self._tdms_writer.write_segment([self._root_obj, self._raw_group_obj])
            self._tdms_writer.write_segment([self._root_obj, self._filt_group_obj])
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

    def _write_tdms(self, raw: np.ndarray, filtered: np.ndarray):
        # Create a TDMS-compatible list of ChannelObjects with filtered data
        try:
            channel_objects = []

            for i in range(len(DAQConfig.channel_names)):
                channel_objects.append(
                    ChannelObject(
                        self._raw_group_obj.group, DAQConfig.channel_names[i], raw[i, :]
                    )
                )
                channel_objects.append(
                    ChannelObject(
                        self._filt_group_obj.group,
                        DAQConfig.channel_names[i],
                        filtered[i, :],
                    )
                )

            self._tdms_writer.write_segment(channel_objects)

        except Exception as e:
            logging.error(f"[DAQ] TDMS Writing exceptions : {e}")

    def close(self):
        # Close the DAQ task
        logging.debug("[DAQ] Closing DAQ task...")
        self._task.close()

        logging.debug("[DAQ] Disconnecting from MQTT...")
        self.mqtt_disconnect()

        logging.debug("[DAQ] Closing TDMS file...")
        self._close_tdms()

    @classmethod
    def run(cls, logger_config: LoggerConfig, stop_event: Event):  # type: ignore
        initialize_logging(
            process_name=logger_config.log_name,
            broker=logger_config.mqtt_config.host_name,
            port=logger_config.mqtt_config.host_port,
        )

        logging.debug("[DAQ] Starting the DAQ Worker")
        daq = DAQ.get_instance(logger_config=logger_config)

        while not stop_event.is_set():
            time.sleep(1)

        logging.debug("[DAQ] Stopping the DAQ Worker")
        daq.close()
