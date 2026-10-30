#!/usr/bin/env python3
"""Fake NCM DAQ for testing the real MCU + bridge, plus a console to drive it.

Only the DAQ is simulated. The MCUs and bridges are the real ones.

    pip install "paho-mqtt<2.0"

    python3 daq_sim.py                      # broker on localhost
    python3 daq_sim.py --host 10.10.0.100

The fake DAQ behaves like NCM_Daq:
    NCM/Experiment/Start   -> start recording (repeats while recording are ignored)
    NCM/Experiment/Stop    -> stop recording
    NCM/Experiment/Rename  -> stop recording, set the file name (plain string)
    while recording        -> NCM/DisplayData + NCM/Experiment/Elapsed at 10 Hz

It also watches what the bridges send:
    NCM/MCU/DisplayData    -> rate, last values and malformed messages per location
    logs/global/MCU-*      -> the bridges' log lines (INFO and above)

Console commands (type + Enter), stand-ins for the GUI buttons:
    p           publish NCM/Experiment/Prepare
    s           publish NCM/Experiment/Stop
    r <name>    publish NCM/Experiment/Rename
    st          print the status table now
    q           quit

Ctrl-C also quits.
"""

import argparse
import json
import math
import random
import sys
import threading
import time

from paho.mqtt.client import Client, MQTTv5

# ---------------------------------------------------------------- topics

BASE = "NCM"
EXP = f"{BASE}/Experiment"
PREPARE_TOPIC = f"{EXP}/Prepare"
START_TOPIC = f"{EXP}/Start"
STOP_TOPIC = f"{EXP}/Stop"
RENAME_TOPIC = f"{EXP}/Rename"
ELAPSED_TOPIC = f"{EXP}/Elapsed"

DAQ_TOPIC = f"{BASE}/DisplayData"
MCU_TOPIC = f"{BASE}/MCU/DisplayData"  # what the bridge publishes
LOG_TOPIC = "logs/global/+"  # GenericMqtteLogger: logs/<system>/<process>

LOCATIONS = ("LL", "LQ", "RQ", "RR")

STOP = threading.Event()
PRINT_LOCK = threading.Lock()


def log(tag: str, text: str) -> None:
    with PRINT_LOCK:
        print(f"{time.strftime('%H:%M:%S')} [{tag}] {text}", flush=True)


def wave(period_s, low, high, phase=0.0, noise=0.0):
    mid, amp = (low + high) / 2.0, (high - low) / 2.0
    v = mid + amp * math.sin(2 * math.pi * time.time() / period_s + phase)
    return v + (random.uniform(-noise, noise) if noise else 0.0)


# ---------------------------------------------------------------- MCU monitor


class McuStats:
    """Per-location counters for NCM/MCU/DisplayData."""

    def __init__(self):
        self.count = 0
        self.window = []  # arrival times in the last few seconds
        self.last = None
        self.last_time = 0.0
        self.first_after_start = None  # s from DAQ start to the first message

    def add(self, payload: dict, now: float) -> None:
        self.count += 1
        self.window.append(now)
        self.window = [t for t in self.window if now - t <= 3.0]
        self.last = payload
        self.last_time = now

    def rate(self, now: float) -> float:
        recent = [t for t in self.window if now - t <= 3.0]
        return len(recent) / 3.0


# ---------------------------------------------------------------- fake DAQ


class DaqSim:
    PHASES = {"LL": 0.0, "LQ": 0.7, "RQ": 1.4, "RR": 2.1}

    def __init__(self, host: str, port: int, rate: float):
        self._host, self._port, self._rate = host, port, rate
        self._client = Client(client_id=f"sim-daq-{random.randint(1000, 9999)}", protocol=MQTTv5)
        self._client.on_connect = self._on_connect
        self._client.on_disconnect = lambda *a, **k: log("daq", "disconnected from broker")

        self._lock = threading.Lock()
        self._recording = False
        self._t0 = 0.0
        self._file_name = "default"
        self._prepare_time = None
        self._starts_this_run = 0

        self._mcu = {loc: McuStats() for loc in LOCATIONS}
        self._bad_mcu = 0

    # ---------------------------------------------------------- MQTT

    def _on_connect(self, client, userdata, flags, rc, properties=None):
        log("daq", f"connected to {self._host}:{self._port}")
        handlers = {
            PREPARE_TOPIC: self._on_prepare,
            START_TOPIC: self._on_start,
            STOP_TOPIC: self._on_stop,
            RENAME_TOPIC: self._on_rename,
            MCU_TOPIC: self._on_mcu_data,
            LOG_TOPIC: self._on_log,
        }
        for topic, handler in handlers.items():
            client.subscribe(topic)
            client.message_callback_add(topic, handler)

    def _on_prepare(self, c, u, msg):
        with self._lock:
            self._prepare_time = time.time()
            self._starts_this_run = 0
        log("exp", "Prepare seen")

    def _on_start(self, c, u, msg):
        now = time.time()
        with self._lock:
            self._starts_this_run += 1
            since = f" ({now - self._prepare_time:.1f} s after Prepare)" if self._prepare_time else ""
            if self._recording:
                log("daq", f"Start #{self._starts_this_run}{since} - already recording, ignored")
                return
            self._recording = True
            self._t0 = now
            for s in self._mcu.values():
                s.first_after_start = None
        log("daq", f"Start #{self._starts_this_run}{since} - RECORDING to '{self._file_name}.tdms'")

    def _on_stop(self, c, u, msg):
        with self._lock:
            was = self._recording
            self._recording = False
            elapsed = time.time() - self._t0
        if was:
            log("daq", f"Stop - recording ended after {elapsed:.1f} s")
            self.print_status()
        else:
            log("daq", "Stop - not recording, ignored")

    def _on_rename(self, c, u, msg):
        name = msg.payload.decode(errors="replace")
        with self._lock:
            was = self._recording
            self._recording = False  # the real DAQ stops its NI task on Rename
            self._file_name = name
        log("daq", f"Rename -> '{name}'" + (" - recording STOPPED (like the real DAQ)" if was else ""))

    def _on_mcu_data(self, c, u, msg):
        now = time.time()
        try:
            data = json.loads(msg.payload.decode())
            loc = data["Location"]
            p = data["Pressure"]
            float(p["DP"]), float(p["CH1"]), float(p["CH2"]), float(data["Velocity"])
            if loc not in self._mcu:
                raise ValueError(f"unknown location {loc!r}")
        except (ValueError, KeyError, TypeError) as e:
            self._bad_mcu += 1
            log("mcu", f"malformed DisplayData ({e!r}): {msg.payload[:120]!r}")
            return

        with self._lock:
            stats = self._mcu[loc]
            if stats.count == 0 or now - stats.last_time > 2.0:
                log("mcu", f"{loc} data started")
            if self._recording and stats.first_after_start is None:
                stats.first_after_start = now - self._t0
            stats.add(data, now)

    def _on_log(self, c, u, msg):
        process = msg.topic.rsplit("/", 1)[-1]
        if not process.startswith("MCU"):
            return
        try:
            entry = json.loads(msg.payload.decode())
        except ValueError:
            return
        level = entry.get("level", "")
        if level == "DEBUG":
            return
        code = f" {entry['error_code']}" if "error_code" in entry else ""
        # CustomFormatter puts "LEVEL  code  " in front of the message; drop it
        text = entry.get("message", "").split("[MCU]", 1)
        text = "[MCU]" + text[1] if len(text) == 2 else entry.get("message", "")
        log(process, f"{level}{code} {text.strip()}")

    # ---------------------------------------------------------- output

    def print_status(self):
        now = time.time()
        with self._lock:
            state = f"RECORDING {now - self._t0:.1f} s" if self._recording else "idle"
            rows = []
            for loc, s in self._mcu.items():
                if s.count == 0:
                    rows.append(f"  {loc}: no data")
                    continue
                age = now - s.last_time
                p, v = s.last["Pressure"], s.last["Velocity"]
                lag = f", first msg {s.first_after_start:.1f} s after Start" if s.first_after_start is not None else ""
                rows.append(
                    f"  {loc}: {s.rate(now):4.1f} Hz, {s.count} msgs, last {age:.1f} s ago | "
                    f"DP {p['DP']:7.2f}  CH1 {p['CH1']:8.2f}  CH2 {p['CH2']:8.2f}  V {v:6.2f}{lag}"
                )
        with PRINT_LOCK:
            print(f"---- DAQ {state}, file '{self._file_name}', malformed MCU msgs: {self._bad_mcu}")
            print("\n".join(rows), flush=True)

    def publish(self, topic, payload=""):
        self._client.publish(topic, payload)

    # ---------------------------------------------------------- run

    def run(self, status_every: float):
        try:
            self._client.connect(self._host, self._port)
        except Exception as e:
            log("daq", f"connect failed: {e}")
            STOP.set()
            return
        self._client.loop_start()

        next_status = time.time() + status_every
        while not STOP.is_set():
            with self._lock:
                recording, t0 = self._recording, self._t0
            if recording:
                usd = {k: round(wave(9.0, 150, 700, ph, noise=3)) for k, ph in DaqSim.PHASES.items()}
                anm = {k: round(wave(6.0, 0.04, 5.0, ph + 0.4, noise=0.05), 2) for k, ph in DaqSim.PHASES.items()}
                self.publish(DAQ_TOPIC, json.dumps({
                    "Ultra_Sonic_Distance": {k: float(v) for k, v in usd.items()},
                    "Anemometer": anm,
                    "Standing_Wave": {"Left": float(usd["LL"] - usd["LQ"]),
                                      "Right": float(usd["RR"] - usd["RQ"])},
                }))
                self.publish(ELAPSED_TOPIC, f"{time.time() - t0:.1f}")

            if status_every > 0 and time.time() >= next_status:
                if recording or any(time.time() - s.last_time < status_every for s in self._mcu.values()):
                    self.print_status()
                next_status = time.time() + status_every
            STOP.wait(self._rate)

        self._client.loop_stop()
        self._client.disconnect()
        log("daq", "stopped")


# ---------------------------------------------------------------- console


def console(daq: DaqSim):
    for line in sys.stdin:
        cmd, _, arg = line.strip().partition(" ")
        if cmd == "p":
            daq.publish(PREPARE_TOPIC)
        elif cmd == "s":
            daq.publish(STOP_TOPIC)
        elif cmd == "r":
            if not arg:
                log("console", "usage: r <name>")
                continue
            daq.publish(RENAME_TOPIC, arg)
        elif cmd == "st":
            daq.print_status()
        elif cmd == "q":
            break
        elif cmd:
            log("console", "commands: p | s | r <name> | st | q")
    STOP.set()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--host", default="localhost")
    ap.add_argument("--port", type=int, default=1883)
    ap.add_argument("--rate", type=float, default=0.1, help="seconds between DAQ messages (default 0.1 = 10 Hz)")
    ap.add_argument("--status", type=float, default=5.0, help="status table every N s while data flows (0 = off)")
    ap.add_argument("--no-console", action="store_true", help="don't read commands from stdin")
    args = ap.parse_args()

    daq = DaqSim(args.host, args.port, args.rate)
    worker = threading.Thread(target=daq.run, args=(args.status,), daemon=True)
    worker.start()

    if not args.no_console and sys.stdin.isatty():
        log("console", "commands: p (Prepare) | s (Stop) | r <name> (Rename) | st (status) | q (quit)")
        threading.Thread(target=console, args=(daq,), daemon=True).start()

    try:
        while not STOP.is_set():
            time.sleep(0.2)
    except KeyboardInterrupt:
        STOP.set()
    worker.join(timeout=2.0)


if __name__ == "__main__":
    main()
