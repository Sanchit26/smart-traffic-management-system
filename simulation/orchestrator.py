import time, argparse
from pathlib import Path
from common.ioutils import read_latest_json, write_json_atomic
from controllers.rule_based import RuleBasedController
from controllers.rl_agent import RLAgent
from settings import config
import requests  # Add this import

COUNTS_FILE = config["save_counts"]
PLAN_FILE = config["plan_file"]
BACKEND_URL = "http://localhost:5000"

def run(controller_type="rl"):
    controller = RuleBasedController() if controller_type == "rule" else RLAgent()
    print(f"✅ Controller running: {controller.__class__.__name__}")

    while True:
        latest = read_latest_json(COUNTS_FILE)
        if not latest:
            time.sleep(1)
            continue

        lane_counts = latest["lane_counts"]
        plan = controller.decide(lane_counts)
        write_json_atomic(PLAN_FILE, {"plan": plan})

        print(f"🟢 New signal plan: {plan}")

        # Post event to Flask backend
        try:
            event = {"timestamp": time.time(), "plan": plan, "lane_counts": lane_counts}
            requests.post(f"{BACKEND_URL}/events", json=event, timeout=1)
        except Exception as e:
            print(f"[WARN] Could not post event to backend: {e}")

        time.sleep(2)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["rule", "rl"], default="rl")
    args = parser.parse_args()
    run(controller_type=args.mode)
