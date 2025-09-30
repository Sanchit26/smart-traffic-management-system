import subprocess
import time
import sys
import os

processes = []

def run_all():
    try:
        print("🚦 Starting Smart Traffic System...")

        env = os.environ.copy()
        env["PYTHONPATH"] = os.getcwd()

        # 1. Start YOLOv8 CV Detection
        p1 = subprocess.Popen([sys.executable, "ai_module/cv_module.py"], env=env)
        processes.append(p1)
        print("✅ CV Detection started.")

        time.sleep(3)  # let CV warm up

    # 2. Start Bridge Provider and Orchestrator ONLY when triggered from dashboard (not auto-started)
    # p2 = subprocess.Popen([sys.executable, "simulation/bridge_provider.py"], env=env)
    # processes.append(p2)
    # print("✅ Bridge provider started.")

    # time.sleep(2)

    # p3 = subprocess.Popen([sys.executable, "simulation/orchestrator.py", "--mode", "rl"], env=env)
    # processes.append(p3)
    # print("✅ Orchestrator started (RL mode).")

    # time.sleep(2)

        # 4. Start Flask Backend (fix path)
        p4 = subprocess.Popen([sys.executable, "app.py"], cwd="dashboard/backend", env=env)
        processes.append(p4)
        print("✅ Flask backend started at http://localhost:5000")

        time.sleep(2)


        # 5. Start React Frontend (npm start) from dashboard/src/ (where the correct package.json is)
        p5 = subprocess.Popen(["npm", "start"], cwd="dashboard/src", env=env)
        processes.append(p5)
        print("✅ React frontend started at http://localhost:3000")

        print("\n🚀 All modules running. Press Ctrl+C to stop.\n")

        # Monitor processes
        while True:
            for i, p in enumerate(processes):
                ret = p.poll()
                if ret is not None:
                    print(f"[ERROR] Process {i+1} exited with code {ret}")
            time.sleep(5)

    except KeyboardInterrupt:
        print("\n🛑 Shutting down all processes...")
        for p in processes:
            p.terminate()
        print("✅ All stopped.")

if __name__ == "__main__":
    run_all()
