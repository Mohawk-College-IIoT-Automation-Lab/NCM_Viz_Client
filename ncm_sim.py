#!/usr/bin/env python3
"""NCM test publishers - fake DAQ, MCUs and SEN units for GUI development.

No hardware, no NI drivers, no Dynamixels. Just a broker.

    pip install paho-mqtt

    python3 ncm_sim.py all                  # 6 clients: daq + 4 mcu + sen
    python3 ncm_sim.py daq
    python3 ncm_sim.py mcu LL
    python3 ncm_sim.py sen
    python3 ncm_sim.py all --host 192.168.1.50 --rate 0.1

Every client connects separately with its own client id, exactly as the real
units do. Payload shapes mirror include/DataStructures.py - if you change a
model there, change it here too.

Ctrl-C stops everything.
"""

import argparse
import json
import math
import random
import signal
import threading
import time

from paho.mqtt.client import Client, MQTTv5


# ---------------------------------------------------------------- topics

BASE = "NCM"
EXP = f"{BASE}/Experiment"
START_TOPIC = f"{EXP}/Start"
STOP_TOPIC = f"{EXP}/Stop"
RENAME_TOPIC = f"{EXP}/Rename"
ELAPSED_TOPIC = f"{EXP}/Elapsed"

DAQ_TOPIC = f"{BASE}/DisplayData"
MCU_TOPIC = f"{BASE}/DisplayData/MCU"

SEN_BASE = f"{BASE}/SEN"
LOCATIONS = ("LL", "LQ", "RQ", "RR")
PORTS = ("LEFT", "RIGHT")


# ---------------------------------------------------------------- helpers

STOP = threading.Event()


def wave(period_s, low, high, phase=0.0, noise=0.0):
    """Sine between low and high, plus optional uniform noise."""
    mid = (low + high) / 2.0
    amp = (high - low) / 2.0
    v = mid + amp * math.sin(2 * math.pi * time.time() / period_s + phase)
    if noise:
        v += random.uniform(-noise, noise)
    return v


def clamp(v, low, high):
    return max(low, min(high, v))


class SimClient:
    """One paho client on its own thread, publishing at a fixed rate."""

    def __init__(self, name, host, port, rate):
        self.name = name
        self.rate = rate
        self._client = Client(client_id=f"sim-{name}-{random.randint(1000, 9999)}",
                              protocol=MQTTv5)
        self._client.on_connect = self._on_connect
        self._host = host
        self._port = port

    def _on_connect(self, client, userdata, flags, rc, properties=None):
        print(f"[{self.name}] connected to {self._host}:{self._port}")
        self.on_connect(client)

    # --- override these ---
    def on_connect(self, client):
        pass

    def tick(self):
        raise NotImplementedError

    def run(self):
        try:
            self._client.connect(self._host, self._port)
        except Exception as e:
            print(f"[{self.name}] connect failed: {e}")
            return
        self._client.loop_start()
        while not STOP.is_set():
            try:
                self.tick()
            except Exception as e:
                print(f"[{self.name}] tick error: {e}")
            STOP.wait(self.rate)
        self._client.loop_stop()
        self._client.disconnect()
        print(f"[{self.name}] stopped")

    def pub(self, topic, payload):
        if isinstance(payload, (dict, list)):
            payload = json.dumps(payload)
        self._client.publish(topic, payload)


# ---------------------------------------------------------------- DAQ

class DaqSim(SimClient):
    """Publishes SensorData on NCM/DisplayData and an elapsed counter.

    Publishes continuously so the GUI shows life without pressing Start.
    Start/Stop only reset and gate the elapsed counter, and Rename is logged
    so you can see the command land.
    """

    PHASES = {"LL": 0.0, "LQ": 0.7, "RQ": 1.4, "RR": 2.1}

    def __init__(self, host, port, rate):
        super().__init__("daq", host, port, rate)
        self._t0 = time.time()
        self._running = True

    def on_connect(self, client):
        for t in (START_TOPIC, STOP_TOPIC, RENAME_TOPIC):
            client.subscribe(t)
        client.message_callback_add(START_TOPIC, self._on_start)
        client.message_callback_add(STOP_TOPIC, self._on_stop)
        client.message_callback_add(RENAME_TOPIC, self._on_rename)

    def _on_start(self, c, u, msg):
        self._t0 = time.time()
        self._running = True
        print("[daq] experiment START")

    def _on_stop(self, c, u, msg):
        self._running = False
        print("[daq] experiment STOP")

    def _on_rename(self, c, u, msg):
        print(f"[daq] rename -> {msg.payload.decode()!r}")

    def tick(self):
        usd = {loc: round(wave(9.0, 150, 700, ph, noise=3))
               for loc, ph in DaqSim.PHASES.items()}
        anm = {loc: round(wave(6.0, 0.04, 5.0, ph + 0.4, noise=0.05), 2)
               for loc, ph in DaqSim.PHASES.items()}

        payload = {
            "Ultra_Sonic_Distance": {k: float(v) for k, v in usd.items()},
            "Anemometer": anm,
            "Standing_Wave": {
                "Left": float(usd["LL"] - usd["LQ"]),
                "Right": float(usd["RR"] - usd["RQ"]),
            },
        }
        self.pub(DAQ_TOPIC, payload)

        if self._running:
            self.pub(ELAPSED_TOPIC, f"{time.time() - self._t0:.1f}")


# ---------------------------------------------------------------- MCU

class McuSim(SimClient):
    """One MCU for one location. All four share NCM/DisplayData/MCU."""

    PHASES = {"LL": 0.0, "LQ": 0.9, "RQ": 1.8, "RR": 2.7}

    def __init__(self, location, host, port, rate):
        super().__init__(f"mcu-{location}", host, port, rate)
        self.location = location
        self.phase = McuSim.PHASES[location]

    def tick(self):
        # Velocity: signed, well inside the -5..+5 display range.
        velocity = wave(7.0, -4.5, 4.5, self.phase, noise=0.08)

        # Two absolute pressure taps per location, inside 950..1200 mbar.
        ch1 = wave(11.0, 985, 1165, self.phase, noise=2.0)
        ch2 = wave(11.0, 985, 1165, self.phase + 0.5, noise=2.0)

        self.pub(MCU_TOPIC, {
            "Location": self.location,
            "Pressure": {
                "DP": round(ch1 - ch2, 2),
                "CH1": round(ch1, 1),
                "CH2": round(ch2, 1),
            },
            "Velocity": round(velocity, 2),
        })


# ---------------------------------------------------------------- SEN

def base_telemetry(mm, position, percent, moving):
    return {
        "pwm": int(clamp(random.gauss(300 if moving else 0, 40), -885, 885)),
        "current": int(clamp(random.gauss(120 if moving else 15, 25), -1193, 1193)),
        "velocity": int(random.gauss(180 if moving else 0, 30)),
        "position": int(position),
        "percent": int(percent),
        "mm": round(mm, 2),
    }


def sen_config(port, sen_id):
    return {
        "port": port,
        "id": sen_id,
        "baud_rate": {"baud": 57600, "id": 1},
        "drive_mode": 0,
        "op_mode": 3,
        "moving_threshold": 10,
        "temp_limit": 80,
        "volt_limit": {"min": 95, "max": 160},
        "pwm_limit": 885,
        "current_limit": 1193,
        "velocity_limit": 200,
        "position_limit": {"min": 0, "max": 4095},
        "velocity_pid": {"P": 100, "I": 1920, "D": 0},
        "position_pid": {"P": 800, "I": 0, "D": 0},
        "FFGain1": 0,
        "FFGain2": 0,
        "mappings": [
            {"mm": 0.0, "position": 0},
            {"mm": 100.0, "position": 2048},
            {"mm": 200.0, "position": 4095},
        ],
        "direction": port == "LEFT",
        "torque_en": True,
    }


class SenSim(SimClient):
    """Both SEN ports on one client, as a single control module would be.

    Follows goal commands so the SEN tab actually reacts to the jog and
    move buttons, and answers get_config with a full SenConfigModel.
    """

    MM_MIN = 0.0
    MM_MAX = 200.0
    POS_MAX = 4095
    SPEED_MM_S = 40.0

    def __init__(self, host, port, rate):
        super().__init__("sen", host, port, rate)
        self._state = {p: {"mm": 100.0, "goal": 100.0} for p in PORTS}
        self._lock = threading.Lock()
        self._last = time.time()

    def on_connect(self, client):
        for p in PORTS:
            base = f"{SEN_BASE}/{p}"
            for leaf in ("goal/mm", "goal/position", "goal/percent",
                         "jog", "jog_percent", "stop", "set_home",
                         "get_config"):
                topic = f"{base}/{leaf}"
                client.subscribe(topic)
                client.message_callback_add(
                    topic, self._make_handler(p, leaf))

    def _make_handler(self, port, leaf):
        def handler(c, u, msg):
            raw = msg.payload.decode().strip()
            with self._lock:
                st = self._state[port]
                try:
                    if leaf == "goal/mm":
                        st["goal"] = clamp(float(raw), SenSim.MM_MIN, SenSim.MM_MAX)
                    elif leaf == "goal/position":
                        st["goal"] = clamp(
                            float(raw) / SenSim.POS_MAX * SenSim.MM_MAX,
                            SenSim.MM_MIN, SenSim.MM_MAX)
                    elif leaf == "goal/percent":
                        st["goal"] = clamp(float(raw) / 100.0 * SenSim.MM_MAX,
                                           SenSim.MM_MIN, SenSim.MM_MAX)
                    elif leaf == "jog":
                        st["goal"] = clamp(
                            st["goal"] + float(raw) / SenSim.POS_MAX * SenSim.MM_MAX,
                            SenSim.MM_MIN, SenSim.MM_MAX)
                    elif leaf == "jog_percent":
                        st["goal"] = clamp(
                            st["goal"] + float(raw) / 100.0 * SenSim.MM_MAX,
                            SenSim.MM_MIN, SenSim.MM_MAX)
                    elif leaf == "stop":
                        st["goal"] = st["mm"]
                    elif leaf == "set_home":
                        st["goal"] = 0.0
                    elif leaf == "get_config":
                        sen_id = 1 if port == "LEFT" else 2
                        self.pub(f"{SEN_BASE}/{port}/config",
                                 sen_config(port, sen_id))
                        print(f"[sen] {port} config sent")
                        return
                except ValueError:
                    print(f"[sen] {port} {leaf}: bad payload {raw!r}")
                    return
            print(f"[sen] {port} {leaf} -> goal {self._state[port]['goal']:.1f} mm")
        return handler

    def tick(self):
        now = time.time()
        dt = now - self._last
        self._last = now

        with self._lock:
            for port in PORTS:
                st = self._state[port]
                delta = st["goal"] - st["mm"]
                step = SenSim.SPEED_MM_S * dt
                moving = abs(delta) > 0.05
                if moving:
                    st["mm"] += math.copysign(min(step, abs(delta)), delta)

                mm = st["mm"]
                goal_mm = st["goal"]
                pos = mm / SenSim.MM_MAX * SenSim.POS_MAX
                goal_pos = goal_mm / SenSim.MM_MAX * SenSim.POS_MAX
                pct = mm / SenSim.MM_MAX * 100.0
                goal_pct = goal_mm / SenSim.MM_MAX * 100.0

                self.pub(f"{SEN_BASE}/{port}/telemetery/json", {
                    "goal_telemetry": base_telemetry(
                        goal_mm, goal_pos, goal_pct, moving),
                    "moving": 1 if moving else 0,
                    "moving_status": 0x01 if moving else 0x00,
                    "present_telemetry": base_telemetry(mm, pos, pct, moving),
                    "velocity_trajectory": int(random.gauss(150, 20)) if moving else 0,
                    "position_trajectory": int(goal_pos),
                    "present_input_voltage": int(random.gauss(120, 2)),
                    "present_temp": int(random.gauss(34, 1.5)),
                })


# ---------------------------------------------------------------- main

def build(role, args):
    if role == "daq":
        return [DaqSim(args.host, args.port, args.rate)]
    if role == "sen":
        return [SenSim(args.host, args.port, args.rate)]
    if role == "mcu":
        locs = args.locations or list(LOCATIONS)
        return [McuSim(loc, args.host, args.port, args.rate) for loc in locs]
    if role == "all":
        return (build("daq", args) + build("mcu", args) + build("sen", args))
    raise SystemExit(f"unknown role: {role}")


def main():
    ap = argparse.ArgumentParser(description="NCM MQTT test publishers")
    ap.add_argument("role", choices=["all", "daq", "mcu", "sen"])
    ap.add_argument("locations", nargs="*", choices=list(LOCATIONS) + [],
                    help="for role 'mcu': which locations (default all four)")
    ap.add_argument("--host", default="localhost")
    ap.add_argument("--port", type=int, default=1883)
    ap.add_argument("--rate", type=float, default=0.1,
                    help="seconds between messages (default 0.1 = 10 Hz)")
    args = ap.parse_args()

    sims = build(args.role, args)

    signal.signal(signal.SIGINT, lambda *_: STOP.set())
    signal.signal(signal.SIGTERM, lambda *_: STOP.set())

    threads = [threading.Thread(target=s.run, daemon=True, name=s.name)
               for s in sims]
    for t in threads:
        t.start()

    print(f"running {len(sims)} client(s) at {1 / args.rate:.0f} Hz - Ctrl-C to stop")
    try:
        while not STOP.is_set():
            time.sleep(0.2)
    except KeyboardInterrupt:
        STOP.set()

    for t in threads:
        t.join(timeout=2.0)


if __name__ == "__main__":
    main()
