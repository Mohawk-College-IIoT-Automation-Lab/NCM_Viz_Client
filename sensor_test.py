import nidaqmx
import time

import nidaqmx.task

SAMPLE_RATE = 1000  # Hz
SAMPLES_PER_READ = 1000  # One second worth of data
CHANNEL = "Dev2/ai1"  # Change Dev1 to your actual device name
FILE_NAME = "daq_data.txt"

task = nidaqmx.Task()

def main():
    # Set up the channel and timing
    task.ai_channels.add_ai_voltage_chan(CHANNEL)
    task.timing.cfg_samp_clk_timing(rate=SAMPLE_RATE,
                                    sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS,
                                    samps_per_chan=SAMPLES_PER_READ)
    
    print("Starting data collection. Press Ctrl+C to stop.")
    task.start()

    while True:
        # Start task and read data
       
       #Todo: make this work
        data = task.ai_channels
        data = task.read()
    
        # Write data to file
        with open(FILE_NAME, "a") as f:
            for sample in data:
                f.write(f"{sample:.6f}\n")
        
        print(f"Wrote {SAMPLES_PER_READ} samples to {FILE_NAME}")
        time.sleep(1)  # Wait before next capture (if needed)

if __name__ == "__main__":
    
    main()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Exiting...")
        task.stop()
        
