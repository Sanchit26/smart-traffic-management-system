#!/usr/bin/env python3
"""
Manual Simulation Launcher - Starts the manual simulation
"""

import os
import subprocess
import sys
import time

def check_backend():
    """Check if backend is running"""
    import requests
    try:
        response = requests.get('http://localhost:5050/api/traffic-data', timeout=2)
        return response.status_code == 200
    except:
        return False

def main():
    print("🚀 Manual Traffic Simulation Launcher")
    print("=" * 50)
    
    # Check if backend is running
    print("🔍 Checking dashboard backend...")
    if check_backend():
        print("✅ Backend is running on port 5050")
    else:
        print("⚠️  Backend not detected - simulation will run in standalone mode")
        print("   Start the dashboard backend for full integration")
    
    # Check if frontend is running
    print("🔍 Checking dashboard frontend...")
    try:
        import requests
        response = requests.get('http://localhost:3001', timeout=2)
        print("✅ Frontend is running on port 3001")
    except:
        print("⚠️  Frontend not detected - manual control will be limited")
        print("   Start the dashboard frontend to use manual controls")
    
    print("\n🎮 Starting Manual Simulation...")
    print("📋 Instructions:")
    print("   • Use the Dashboard Manual Control panel to control signals")
    print("   • Or use keyboard controls (1-4 to cycle signals, Space to spawn vehicles)")
    print("   • Close the simulation window to exit")
    print("\n" + "=" * 50)
    
    # Change to simulation directory
    simulation_dir = "/Users/syedasif/final-final/simulation"
    os.chdir(simulation_dir)
    
    # Run the manual simulation
    python_exe = "/Users/syedasif/final-final/.venv/bin/python"
    simulation_script = "manual_simulation.py"
    
    try:
        subprocess.run([python_exe, simulation_script])
    except KeyboardInterrupt:
        print("\n🛑 Simulation stopped by user")
    except Exception as e:
        print(f"❌ Error running simulation: {e}")

if __name__ == "__main__":
    main()