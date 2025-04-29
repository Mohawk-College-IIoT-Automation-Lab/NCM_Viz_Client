from multiprocessing import Process
import threading
import time
from .GenericMqtteLogger import Logger
from .DAQ import DAQ

class DAQ_Process(Process):
    
    def __init__(self, name:str="Name", host_name:str="localhost", host_port:int=1883, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.host_name = host_name
        self.host_port = host_port

        self.logger = Logger("DAQ").logger

        self.logger.debug(f"[DAQ Process][init] Process {name} initialized.")

        self._is_running = False
        self._lock = None
        self.name = name

        self._daq = None

    def start(self):
        self._is_running = True
        super().start()
        self.logger.debug(f"[DAQ Process] Process {self.name} started.")
        #self.mqtt_connect()

    def stop(self):
        self._is_running = False
        self.join()
        self.logger.debug(f"[DAQ Process] Process {self.name} stopped.")
        #self.mqtt_disconnect()

    def run(self):
        self._lock = threading.Lock()
        self._daq = DAQ(host_name=self.host_name, host_port=self.host_port)

        while self._is_running:
            time.sleep(0.1)

        self._daq.close()