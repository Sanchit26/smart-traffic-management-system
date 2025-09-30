"""
Bridge provider for integrating real-time CV lane counts with the Pygame simulation.

How it works:
- Reads the latest JSON object from data/ai_module/vehicle_counts.jsonl
- Maps it into the provider schema expected by integrated_simulation.register_detection_provider
- Runs the simulation in RL mode so green times are driven by real counts

Notes:
- This bridges counts into GREEN TIME decisions; it does not spawn/destroy exact sprites.
- If you want the simulation to show exactly N vehicles, we can add a queue-sync later.
"""

import sys
import time
import json
from pathlib import Path
from typing import Dict, Any

# Resolve paths
THIS_DIR = Path(__file__).resolve().parent
REPO_ROOT = THIS_DIR.parent
CV_COUNTS_PATH = REPO_ROOT / "ai_module" / "vehicle_counts.jsonl"

# Import integrated simulation
sys.path.insert(0, str(THIS_DIR))
import integrated_simulation as sim  # type: ignore


def read_latest_jsonl(path: Path) -> Dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        with path.open("r", encoding="utf-8") as f:
            lines = [ln.strip() for ln in f if ln.strip()]
            if not lines:
                return None
            return json.loads(lines[-1])  # last JSON object
    except Exception as e:
        print(f"⚠️ Failed to read {path}: {e}")
        return None


def map_counts_to_provider_payload(latest: Dict[str, Any]) -> Dict[str, Any]:
    """
    Input (from cv_module):
        {"lane_counts": {"lane_1": N1, "lane_2": N2, ...}}

    Output (provider schema for simulation):
    {
      "counts": {
        "right": {"lane0": int, "lane1": int, "lane2": int},
        "down": {"lane0": 0, "lane1": 0, "lane2": 0},
        "left": {"lane0": 0, "lane1": 0, "lane2": 0},
        "up": {"lane0": 0, "lane1": 0, "lane2": 0}
      },
      "ambulance": {"direction": "right", "present": False}
    }
    """
    lane_counts = latest.get("lane_counts", {})
    lanes = {k: int(v) for k, v in lane_counts.items()}

    lane0 = lanes.get("lane_1", 0)
    lane1 = lanes.get("lane_2", 0)

    # Aggregate remaining lanes into lane2
    remaining = sum(lanes.get(f"lane_{i}", 0) for i in range(3, 16))
    lane2 = remaining

    zeros = {"lane0": 0, "lane1": 0, "lane2": 0}

    payload = {
        "counts": {
            "right": {"lane0": lane0, "lane1": lane1, "lane2": lane2},
            "down": zeros.copy(),
            "left": zeros.copy(),
            "up": zeros.copy(),
        },
        "ambulance": {"direction": "right", "present": False},
    }
    return payload


# Cache
last_payload: Dict[str, Any] | None = None
last_mtime: float | None = None


def provider(current_green_idx: int, next_green_idx: int) -> Dict[str, Any]:
    """Callable provider that the simulation will use for live counts"""
    global last_payload, last_mtime

    try:
        if CV_COUNTS_PATH.exists():
            st = CV_COUNTS_PATH.stat()
            if last_mtime is None or st.st_mtime > last_mtime:
                latest = read_latest_jsonl(CV_COUNTS_PATH)
                if latest:
                    last_payload = map_counts_to_provider_payload(latest)
                    last_mtime = st.st_mtime
    except Exception as e:
        print(f"⚠️ Provider error: {e}")

    # Fallback to zeros if nothing read yet
    if not last_payload:
        zeros = {"lane0": 0, "lane1": 0, "lane2": 0}
        last_payload = {
            "counts": {
                "right": zeros.copy(),
                "down": zeros.copy(),
                "left": zeros.copy(),
                "up": zeros.copy(),
            },
            "ambulance": {"direction": "right", "present": False},
        }
    return last_payload


def main():
    sim.mode = "rl"
    sim.register_detection_provider(provider)
    print(f"🚦 Bridge running: reading {CV_COUNTS_PATH} -> driving simulation (RL mode)")
    sim.run()


if __name__ == "__main__":
    main()
