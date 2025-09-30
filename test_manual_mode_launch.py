#!/usr/bin/env python3
"""
Test script to verify manual simulation launch functionality
Simulates clicking manual mode toggle from dashboard
"""

import socketio
import time
import json

def test_manual_mode_toggle():
    """Test the manual mode toggle functionality"""
    print("🧪 Testing Manual Mode Toggle -> Simulation Launch")
    print("=" * 55)
    
    # Connect to the backend
    sio = socketio.Client()
    
    try:
        print("🔌 Connecting to dashboard backend...")
        sio.connect('http://localhost:5050')
        print("✅ Connected to backend")
        
        # Listen for simulation status updates
        @sio.on('manual_simulation_status')
        def on_simulation_status(data):
            print(f"📡 Received simulation status: {data}")
        
        # Wait a bit for connection to stabilize
        time.sleep(1)
        
        # Simulate manual mode toggle ON
        print("🎛️ Simulating manual mode toggle ON...")
        toggle_data = {
            'manual_mode': True,
            'timestamp': time.time()
        }
        
        sio.emit('manual_mode_toggle', toggle_data)
        print("✅ Manual mode toggle event sent")
        
        # Wait for response
        print("⏳ Waiting for simulation launch response...")
        time.sleep(3)
        
        # Check if manual simulation is now running
        import subprocess
        result = subprocess.run(['pgrep', '-f', 'manual_simulation'], 
                               capture_output=True, text=True)
        
        if result.returncode == 0:
            pids = result.stdout.strip().split('\n')
            print(f"✅ Manual simulation is running (PIDs: {', '.join(pids)})")
            return True
        else:
            print("❌ Manual simulation is not running")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
    finally:
        sio.disconnect()
        print("🔌 Disconnected from backend")

def main():
    """Main test function"""
    print("🚀 Testing Manual Simulation Auto-Launch Feature")
    print("🎯 When manual mode is enabled, simulation should start automatically")
    print("")
    
    success = test_manual_mode_toggle()
    
    print("\n" + "=" * 55)
    if success:
        print("✅ TEST PASSED: Manual simulation launches when manual mode is enabled!")
        print("🎉 You can now use the dashboard to control the manual simulation")
        print("🌐 Open http://localhost:3000 and try the Manual Control panel")
    else:
        print("❌ TEST FAILED: Manual simulation did not launch")
        print("🔍 Check the backend logs for errors")
    
    return success

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)