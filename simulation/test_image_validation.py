#!/usr/bin/env python3
"""
Simple visual enhancement validation test
Tests image loading without importing the full simulation
"""

import os

def asset_path(*parts):
    """Get path to asset file"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(script_dir, "images", *parts)

def test_image_assets():
    """Test that all required images exist"""
    print("🎨 Manual Simulation Visual Enhancement Validation")
    print("=" * 55)
    
    # Test intersection background
    bg_path = asset_path("intersection.png")
    bg_exists = os.path.exists(bg_path)
    print(f"🛣️  Intersection: {'✅' if bg_exists else '❌'} {bg_path}")
    
    # Test signal images
    signal_results = []
    signal_types = ["red", "yellow", "green"]
    for signal_type in signal_types:
        signal_path = asset_path("signals", f"{signal_type}.png")
        exists = os.path.exists(signal_path)
        signal_results.append(exists)
        print(f"🚦 {signal_type.capitalize()}: {'✅' if exists else '❌'} {signal_path}")
    
    # Test vehicle images
    vehicle_types = ["car", "bus", "truck", "bike", "rickshaw", "ambulance"]
    directions = ["up", "down", "left", "right"]
    
    vehicle_results = []
    print(f"\n🚗 Vehicle Images ({len(vehicle_types)} types × {len(directions)} directions):")
    
    for direction in directions:
        print(f"   📍 {direction.upper()} direction:")
        for vehicle_type in vehicle_types:
            vehicle_path = asset_path(direction, f"{vehicle_type}.png")
            exists = os.path.exists(vehicle_path)
            vehicle_results.append(exists)
            status = "✅" if exists else "❌"
            print(f"      {status} {vehicle_type}")
    
    # Calculate statistics
    total_signals = len(signal_results)
    found_signals = sum(signal_results)
    
    total_vehicles = len(vehicle_results)
    found_vehicles = sum(vehicle_results)
    
    total_assets = 1 + total_signals + total_vehicles  # 1 background + signals + vehicles
    found_assets = (1 if bg_exists else 0) + found_signals + found_vehicles
    
    print(f"\n📊 Asset Summary:")
    print(f"   🛣️  Background: {1 if bg_exists else 0}/1")
    print(f"   🚦 Signals: {found_signals}/{total_signals}")
    print(f"   🚗 Vehicles: {found_vehicles}/{total_vehicles}")
    print(f"   🎯 Total: {found_assets}/{total_assets} ({found_assets/total_assets*100:.1f}%)")
    
    # Final status
    print(f"\n🎉 Status: {'ALL IMAGES READY!' if found_assets == total_assets else 'SOME IMAGES MISSING'}")
    
    if found_assets == total_assets:
        print("✅ Manual simulation ready with full visual enhancements!")
        print("🚀 Run: python simulation/manual_simulation.py")
    else:
        print("⚠️  Some images missing - simulation will use fallback graphics")
    
    return found_assets == total_assets

if __name__ == "__main__":
    test_image_assets()