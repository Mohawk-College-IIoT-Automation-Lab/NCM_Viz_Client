#!/usr/bin/env python3

from inspect import cleandoc
from paho.mqtt.client import Client, MQTTv5
import sys, signal, time, json, logging, os, random

from paho.mqtt.enums import CallbackAPIVersion
from include.DataStructures import (
    SensorData,
    SensorReadings,
    StandingWave,
    SenTelemetry,
    SenConfigModel,
)
from include.Mqtt import MqttClient


LOG_FMT_STR = "[FAKE] -> %s"

_running = True
_client = Client(
    callback_api_version=CallbackAPIVersion.VERSION2,
    client_id="faker",
    protocol=MQTTv5,
)


def _sub_all_topics(client):
    logging.info(LOG_FMT_STR, "Subbing all topics")


def _on_connect(client, userdata, flags, rc, props=None):
    print(f"Connected to broker")
    _sub_all_topics(client)
    client.loop_start()


def _on_disconnect(client, userdata, rc, props=None):
    print("Disconnected to broker")
    _running = False


def handle_signals(*args):
    print("Signal handled")
    _running = False
    _client.disconnect()
    sys.exit(0)


if __name__ == "__main__":
    # handle signals
    signal.signal(signal.SIGINT, handle_signals)
    signal.signal(signal.SIGTERM, handle_signals)

    _client.on_connect = _on_connect
    _client.on_disconnect = _on_disconnect

    _client.connect(host="work-linux", port=1883)

    _start_time = time.time()

    print(f"Start time: {_start_time}")

    while _running:
        usd = SensorReadings(
            LL=float(random.randrange(0, 700)),
            LQ=float(random.randrange(0, 700)),
            RQ=float(random.randrange(0, 700)),
            RR=float(random.randrange(0, 700)),
        )

        anm = SensorReadings(
            LL=float(random.randrange(0, 4)),
            LQ=float(random.randrange(0, 4)),
            RQ=float(random.randrange(0, 4)),
            RR=float(random.randrange(0, 4)),
        )

        sw = StandingWave(Left=usd.LQ - usd.LL, Right=usd.RQ - usd.RR)

        _client.publish(
            f"NCM/DisplayData",
            SensorData(
                Ultra_Sonic_Distance=usd, Anemometer=anm, Standing_Wave=sw
            ).model_dump_json(),
        )

        timer = time.time() - _start_time
        _client.publish(f"NCM/Experiment/Elapsed", timer)

        print("Pubbing ...")
        time.sleep(0.01)
    
    print("Exitting")
    sys.exit(0)
