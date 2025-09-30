"""
Integrated Simulation

This file preserves the visuals and flow of the original simulation (simulation.py)
while adding integration points for an external RL/YOLO detection pipeline.

Key features:
- Two modes: "sim" (default) and "rl" (external counts via provider function or local server)
- Structured event logging (JSON) identical to simulation.py additions
- Optional HTTP posting of events to localhost:5000/events if available
- Emergency preemption (ambulance) and anomaly detection preserved

To keep changes minimal, we import most logic from simulation.py at runtime and override hooks.
"""

import os
import sys
import time
import json
import threading
from typing import Callable, Dict, Optional

# Reuse pygame & core classes/vars by importing the original simulation module
import importlib.util

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SIM_PATH = os.path.join(BASE_DIR, 'simulation.py')

spec = importlib.util.spec_from_file_location('sim_module', SIM_PATH)
sim = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sim)  # type: ignore

# --- Dashboard/event plumbing ---
try:
    import requests  # optional for event posting
except Exception:
    requests = None

POST_EVENTS_URL = os.environ.get('EVENTS_URL', 'http://localhost:5000/events')
POST_EVENTS = os.environ.get('POST_EVENTS', '0') == '1'

# --- Patch original EventLogger.log so ALL events (from sim) go through here ---
_orig_logger_log = sim.EventLogger.log

def _patched_log(event_type, data=None):
    # Forward to original logger which prints JSON and stores in-memory
    _orig_logger_log(event_type, data)
    # Optionally POST to local server for dashboard prototyping
    payload = {"ts": time.time(), "event": event_type}
    if data:
        payload.update(data)
    posted = False
    if POST_EVENTS and requests is not None:
        try:
            resp = requests.post(POST_EVENTS_URL, json=payload, timeout=0.5)
            if resp.status_code == 200:
                posted = True
        except Exception:
            pass
    # Fallback: write event to local file for later pickup if POST fails
    if not posted:
        try:
            import tempfile, os
            tmp_path = os.path.join(tempfile.gettempdir(), "sim_events.jsonl")
            with open(tmp_path, "a") as f:
                f.write(json.dumps(payload) + "\n")
        except Exception:
            pass

# Apply the patch
sim.EventLogger.log = staticmethod(_patched_log)

# --- RL Integration Hooks ---
# A provider callable can be registered to supply live counts and emergency signals.
# Signature: provider(current_green_idx:int, next_green_idx:int) -> dict
# Return example:
# {
#   'counts': {
#       'right': {'lane0': 2, 'lane1': 1, 'lane2': 0},
#       'down':  {...},
#       'left':  {...},
#       'up':    {...}
#   },
#   'ambulance': {'direction': 'right', 'present': True}  # optional
# }

_provider: Optional[Callable[[int, int], Dict]] = None


def register_detection_provider(fn: Callable[[int, int], Dict]):
    global _provider
    _provider = fn


# Monkey-patch: use RL counts if available in setTime
# Integrated RL detection input here
_orig_setTime = sim.setTime

def setTime_patched():
    if _provider is None:
        return _orig_setTime()

    # Integrated RL detection input here: Use external counts to compute green time
    sim.noOfCars = sim.noOfBuses = sim.noOfTrucks = sim.noOfRickshaws = sim.noOfBikes = 0
    payload = _provider(sim.currentGreen, sim.nextGreen)

    counts = payload.get('counts', {})
    dir_name = sim.directionNumbers[sim.nextGreen]
    lane_counts = counts.get(dir_name, {})

    # Expected keys: lane0/lane1/lane2 (lane0 is bikes lane in original logic)
    bikes = int(lane_counts.get('lane0', 0))
    lane1 = int(lane_counts.get('lane1', 0))
    lane2 = int(lane_counts.get('lane2', 0))

    sim.noOfBikes = bikes
    # Approximate distribution for lane1/lane2: cars+buses+trucks+rickshaws
    # Leave to RL for better breakdown in the future
    # For now, map all lane1+lane2 to cars for simplicity
    sim.noOfCars = lane1 + lane2

    greenTime = int((
        (sim.noOfCars * sim.carTime)
        + (sim.noOfRickshaws * sim.rickshawTime)
        + (sim.noOfBuses * sim.busTime)
        + (sim.noOfTrucks * sim.truckTime)
        + (sim.noOfBikes * sim.bikeTime)
    ) / (sim.noOfLanes + 1))

    if greenTime < sim.defaultMinimum:
        greenTime = sim.defaultMinimum
    elif greenTime > sim.defaultMaximum:
        greenTime = sim.defaultMaximum

    sim.signals[(sim.currentGreen + 1) % (sim.noOfSignals)].green = greenTime

    # Emergency hint from provider (ambulance)
    amb = payload.get('ambulance', {})
    if amb.get('present'):
        sim.emergency_active = True
        sim.emergency_direction = amb.get('direction', sim.directionNumbers[sim.currentGreen])
        sim.EventLogger.log('ambulance_detected', {"direction": sim.emergency_direction, "source": "rl"})


sim.setTime = setTime_patched


# Provide a simple CLI switch for mode selection
# python integrated_simulation.py [sim|rl]
mode = 'sim'
if len(sys.argv) > 1 and sys.argv[1] in ('sim', 'rl'):
    mode = sys.argv[1]


def run():
    if mode == 'sim':
        # Plain simulation behavior from original Main class
        sim.Main()
    else:
        # RL mode: we still run original Main but expect an external provider to be registered
        # Users of this module can import register_detection_provider and set a function before run().
        sim.Main()


if __name__ == '__main__':
    run()
