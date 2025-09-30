#!/usr/bin/env python3
"""
Test script for manual simulation - demonstrates basic functionality
"""

import sys
import os

# Add simulation directory to path
sys.path.append('/Users/syedasif/final-final/simulation')

from manual_simulation import ManualSimulation, SIGNAL_RED, SIGNAL_GREEN, SIGNAL_YELLOW

def test_manual_simulation():
    """Test the manual simulation without dashboard connection"""
    print("🧪 Testing Manual Simulation")
    print("=" * 50)
    
    # Create simulation instance
    sim = ManualSimulation()
    
    # Test signal state management
    print("\n🚦 Testing Signal States:")
    print(f"Initial states: {sim.get_signal_states()}")
    
    # Test signal changes
    sim.set_signal_state(0, SIGNAL_GREEN)  # North to Green
    sim.set_signal_state(1, SIGNAL_YELLOW)  # East to Yellow
    print(f"After changes: {sim.get_signal_states()}")
    
    # Test vehicle spawning
    print("\n🚗 Testing Vehicle Spawning:")
    print(f"Initial vehicle count: {len(sim.vehicles)}")
    
    for i in range(5):
        sim.spawn_vehicle()
    print(f"After spawning 5 vehicles: {len(sim.vehicles)}")
    
    # Simulate a few updates
    print("\n⏰ Testing Vehicle Updates:")
    for i in range(3):
        sim.update_vehicles()
        moving_vehicles = [v for v in sim.vehicles if not v.stopped]
        stopped_vehicles = [v for v in sim.vehicles if v.stopped]
        print(f"Update {i+1}: {len(moving_vehicles)} moving, {len(stopped_vehicles)} stopped")
    
    print("\n✅ Manual simulation test completed!")
    print("🎮 Ready for dashboard control integration")
    
    return True

if __name__ == "__main__":
    try:
        test_manual_simulation()
    except Exception as e:
        print(f"❌ Test failed: {e}")
        sys.exit(1)