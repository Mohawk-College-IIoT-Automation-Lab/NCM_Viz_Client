from NI_DAQ.DAQ import DAQConfig, DAQ, Logger
from multiprocessing import Process, Event
import sys
import time

if __name__ == "__main__":

    daq_cofig = DAQConfig(host_name="10.4.8.5", host_port=1883)
    stop_event = Event()

    daq_process = Process(target=DAQ.run, args=(daq_cofig,stop_event))
    daq_process.start()

    for i in range(15):
        time.sleep(1)
        print(i)

    DAQ.stop(stop_event)
    daq_process.join()

              
    
