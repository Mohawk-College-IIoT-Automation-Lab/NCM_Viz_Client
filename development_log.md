# 2026-09-09

## Development Plan

1. Create data schema for MQTT Json sent form MCUs

2. Change MQTT topic tree

3. Create a simulation backend to test the GUI

4. Modify GUI

5. Figure out how to synchronize data with timestamps (message structure)

---

# 2026-09-14

Adding a new sensor measurement to the Viz client. The measurement will be done on a separate device from the DAQ. So, it will require a new topic.

Unit of measurement is pressure in mbar. Unit of interest is velocity in m/s.
The idea is to record the raw data (pressures from both ports + differential), transform pressure to velocity on edge.
Display only velocity, but save everything similarly to the current pipeline.

Current routine:

    1. Get data (200 unfiltered samples)
    2. Filter data (produce 1 value)
    3. Save data raw and filtered
    4. Prepare data for display (averaging)
    5. Publish display data to mqtt

From `_raw_data_callback` in `Daq.py` inside of `NCM_Daq` repo:

```python
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

self.mqtt_client.publish(f"{ExperimentMqttConfig.base_topic}{ExperimentMqttConfig.elapsed_topic}", f"{timer} ms")
```

Current data schema:

```json
{
    "Ultra_Sonic_Distance": { "LL": 0.0, "LQ": 0.0, "RR": 0.0, "RQ": 0.0 },
    "Anemometer": { "LL": 0.0, "LQ": 0.0, "RR": 0.0, "RQ": 0.0 },
    "Standing_Wave": { "Left": 0.0, "Right": 0.0 }
}
```

Current topic: `NCM/DisplayData`

The idea is to modify the current setup as little as possible and to replicate the current schema as closely as possible.

There will be one differential sensor per location, this will yeild 2 pressures and 1 signed velocity at "LL", "LQ", "RQ", "RR" locations.
Ideally will plan for this data to be sent separatly to prepare for the future setup. Right now, the data will be sent over serial to a PC and the PC will publish the msg to mqtt.
In the future, the MCU will be the publisher.

Routine for adding new "standalone" sensor:

    1. Add the topic constant next to DaqDataTopic

    2. Add NewSensorSignal = pyqtSignal(NewSensorData)

    3. In _sub_all_topcis: subscribe + message_callback_add

    4. Write _NewSensorCallback — copy _DaqDataCallback verbatim, including the watchdog lines

    5. Add a Watchdog instance + NewSensorConnectedSignal if you want a liveness indicator
