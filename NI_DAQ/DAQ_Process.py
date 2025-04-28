from multiprocessing import Process
import time
from .Mqtt.GenericMqtteLogger import GenericMQTT, Logger, LoggerSingleton

class DAQ_Process(Process):
    
    def __init__(self, name:str="Name", host_name:str="localhost", host_port:int=1883, logger:Logger=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mqtt_client = GenericMQTT(host_name, host_port, logger=logger)

        if logger is None:
            self.logger = LoggerSingleton().logger
        else:
            self.logger = logger.logger

        self.logger.debug(f"[NI DAQ] Process {name} initialized.")

        self._is_running = False
        self.name = name

    def start(self):
        self._is_running = True
        super().start()
        self.logger.debug(f"Process {self.name} started.")
        #self.mqtt_connect()

    def stop(self):
        self._is_running = False
        self.join()
        self.logger.debug(f"Process {self.name} stopped.")
        #self.mqtt_disconnect()

    def _hf_data_callback(self):
        pass

    def _lf_data_callback(self):
        pass


    def run(self):
        while self._is_running:
            self.logger.debug(f"Process {self.name} is running.")
            # Call the target function here
            # self.target_function()
            time.sleep(1)  