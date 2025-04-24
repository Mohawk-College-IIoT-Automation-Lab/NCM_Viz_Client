from multiprocessing import Process
from m_base_object import *

class M_USB_DAQ_Process(Process, M_Object):
    """
    M_Process is a class that extends the Process class from the multiprocessing module.
    It is designed to run a function in a separate process and handle its termination.
    """
    
    def __init__(self, name:str="Name", host_name:str="localhost", host_port:int=1883, log_name:str="log", *args, **kwargs):
        super().__init__(args=args, kwargs=kwargs, host_name=host_name, host_port=host_port, log_name=log_name)
        self._is_running = False
        self.name = name

    def start(self):
        """
        The start method is overridden to set the _is_running attribute to True when the process starts.
        """
        self._is_running = True
        super().start()
        self.log(f"Process {self.name} started.")
        #self.mqtt_connect()

    def stop(self):
        """
        The stop method is overridden to set the _is_running attribute to False when the process ends.
        """
        self._is_running = False
        self.join()
        self.log(f"Process {self.name} stopped.")
        #self.mqtt_disconnect()

    def _target_function(self):
        """
        The target function is a placeholder for the function that will be executed in the separate process.
        It should be overridden in subclasses to define the specific behavior of the process.
        """
        pass

    def run(self):
        """
        The run method is overridden to execute the target function in a separate process.
        It sets the _is_running attribute to True when the process starts and to False when it ends.
        """
        while self._is_running:
            self.log(f"Process {self.name} is running.")
            # Call the target function here
            # self.target_function()
            time.sleep(1)  