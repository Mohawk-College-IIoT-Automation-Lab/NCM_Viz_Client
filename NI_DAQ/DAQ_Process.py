from multiprocessing import Process
import threading
import time
from .GenericMqtteLogger import Logger
from .DAQ import DAQ

class DAQ_Process:

    def __init__(self, name:str="Name", host_name:str="localhost", host_port:int=1883):
        
        self.host_name = host_name
        self.host_port = host_port

        self.logger = Logger("DAQ").logger
        self.logger.debug(f"[DAQ Process][init] Process {name} initialized.")

        self._is_running = False
        self._lock = None
        self._daq = None
        self.process = None

    def start(self):
        if not self._is_running:
            self._is_running = True
            self.process = Process(target=self.run)
            self.process.start()
            self.logger.debug(f"[DAQ Process] Process started.")
        else:
            self.logger.debug(f"[DAQ Process] Process is already running")
        
    def stop(self):
        self._is_running = False
        self.process.join()
        self.process = None
        self.logger.debug(f"[DAQ Process] Process stopped.")

    def run(self):
        self.logger.debug("[DAQ Process] Trying to lock")
        self._daq = DAQ(host_name=self.host_name, host_port=self.host_port, logger=Logger("DAQ"))

        while self._is_running:
            self._daq.mqtt_client.loop()

        self._daq.close()