import time
from daq import Daq  # Importing the renamed Daq class

def main():
    daq = Daq(client_id="myDaqClient", broker_address="localhost")

    if not daq.connect():
        return 1

    daq.subscribe("Sampling")

    print("Running... Press Ctrl+C to quit.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        daq.stop()
        print("Exiting...")

if __name__ == "__main__":
    main()
