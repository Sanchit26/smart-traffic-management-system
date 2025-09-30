#!/usr/bin/env python3
"""
Test script for visual enhancements in manual simulation
Validates that all images load correctly and simulation runs with graphics
"""

import os
import sys
import pygame

# Add parent directory to path to import simulation modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from simulation.manual_simulation import ManualSimulation, asset_path

def test_image_loading():
    """Test that all required images can be loaded"""
    print("🎨 Testing Visual Enhancement Image Loading")
    print("=" * 50)
    
    # Test intersection background
    bg_path = asset_path("intersection.png")
    print(f"🛣️  Intersection background: {bg_path}")
    if os.path.exists(bg_path):
        print("   ✅ Intersection image found")
    else:
        print("   ❌ Intersection image missing")
    
    # Test signal images
    signal_types = ["red", "yellow", "green"]
    for signal_type in signal_types:
        signal_path = asset_path("signals", f"{signal_type}.png")
        print(f"🚦 Signal {signal_type}: {signal_path}")
        if os.path.exists(signal_path):
            print(f"   ✅ {signal_type.capitalize()} signal image found")
        else:
            print(f"   ❌ {signal_type.capitalize()} signal image missing")
    
    # Test vehicle images
    vehicle_types = ["car", "bus", "truck", "bike", "rickshaw", "ambulance"]
    directions = ["up", "down", "left", "right"]
    
    total_images = 0
    found_images = 0
    
    for direction in directions:
        print(f"🚗 Vehicle images - {direction} direction:")
        for vehicle_type in vehicle_types:
            vehicle_path = asset_path(direction, f"{vehicle_type}.png")
            total_images += 1
            if os.path.exists(vehicle_path):
                print(f"   ✅ {vehicle_type} ({direction})")
                found_images += 1
            else:
                print(f"   ❌ {vehicle_type} ({direction}) - missing")
    
    print(f"\n📊 Image Summary: {found_images}/{total_images} images found")
    print(f"🎯 Coverage: {(found_images/total_images)*100:.1f}%")
    
    return found_images == total_images

def test_simulation_initialization():
    """Test that simulation can initialize with image loading"""
    print("\n🚦 Testing Simulation Initialization")
    print("=" * 50)
    
    try:
        # Initialize pygame (required for image loading)
        pygame.init()
        pygame.display.set_mode((1, 1))  # Minimal display for testing
        
        # Create simulation instance
        simulation = ManualSimulation()
        
        # Check if background loaded
        if simulation.background_image:
            print("✅ Background image loaded successfully")
        else:
            print("⚠️  Background image not loaded (fallback mode)")
        
        # Check signal initialization
        signal_count = len(simulation.signals)
        print(f"✅ {signal_count} traffic signals initialized")
        
        # Test vehicle spawning with image loading
        print("🚗 Testing vehicle spawning with images...")
        initial_count = len(simulation.vehicles)
        
        # Spawn a few test vehicles
        for _ in range(3):
            simulation.spawn_vehicle()
        
        final_count = len(simulation.vehicles)
        spawned = final_count - initial_count
        
        print(f"✅ Spawned {spawned} vehicles successfully")
        
        # Clean up
        pygame.quit()
        
        return True
        
    except Exception as e:
        print(f"❌ Simulation initialization failed: {e}")
        pygame.quit()
        return False

def main():
    """Main test function"""
    print("🧪 Manual Simulation Visual Enhancement Test")
    print("🎨 Testing realistic vehicle and signal images")
    print("=" * 60)
    
    # Test image loading
    images_ok = test_image_loading()
    
    # Test simulation initialization
    sim_ok = test_simulation_initialization()
    
    # Final results
    print("\n🎯 Test Results")
    print("=" * 30)
    
    if images_ok and sim_ok:
        print("✅ All visual enhancement tests passed!")
        print("🎉 Manual simulation ready with realistic graphics")
        print("🚀 You can now run: python simulation/manual_simulation.py")
        return True
    else:
        print("❌ Some tests failed")
        if not images_ok:
            print("   - Image loading issues detected")
        if not sim_ok:
            print("   - Simulation initialization issues detected")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)