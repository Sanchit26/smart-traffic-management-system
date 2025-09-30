#!/usr/bin/env python3
"""
Test script to verify realistic vehicle count changes
"""

import requests
import time
import json

def test_vehicle_counts():
    """Test that vehicle counts change realistically"""
    print("🚗 Testing Realistic Vehicle Count Updates")
    print("=" * 50)
    
    base_url = "http://localhost:5050"
    
    # Test simulation data endpoint
    print("📊 Testing simulation data endpoint...")
    previous_count = None
    
    for i in range(5):
        try:
            response = requests.get(f"{base_url}/api/simulation-data")
            if response.status_code == 200:
                data = response.json()
                current_count = data.get('vehicles_detected', 0)
                
                if previous_count is not None:
                    change = current_count - previous_count
                    print(f"   Check {i+1}: {current_count} vehicles (change: {change:+d})")
                else:
                    print(f"   Check {i+1}: {current_count} vehicles (baseline)")
                
                previous_count = current_count
            else:
                print(f"   ❌ Request failed: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        if i < 4:  # Don't sleep after last iteration
            time.sleep(2)  # Check every 2 seconds
    
    print("\n🎯 Expected behavior:")
    print("   • Vehicle counts should stay relatively stable")
    print("   • Changes should be small (-2 to +5)")
    print("   • Values should be in realistic range (80-200)")
    print("\n✅ Test completed! Check the dashboard for slower, more realistic updates.")

if __name__ == "__main__":
    test_vehicle_counts()