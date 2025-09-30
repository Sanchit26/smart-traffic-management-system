# Manual Traffic Simulation - Dashboard Integration Guide

## � Latest Enhancements - Realistic Visual Experience

### Visual Improvements ✨
- **🚗 Realistic Vehicle Images**: Now uses actual PNG images of cars, buses, trucks, bikes, rickshaws, and ambulances instead of colored rectangles
- **🚦 Traffic Signal Images**: Actual red, yellow, and green signal images for authentic traffic light appearance
- **🛣️ Intersection Background**: Real intersection image for realistic road visualization
- **🔄 Smart Fallback**: Gracefully falls back to colored shapes if images are missing

### Asset Structure
The simulation now uses images from `/simulation/images/` directory:
```
images/
├── intersection.png          # Background intersection image
├── signals/
│   ├── red.png              # Red signal image  
│   ├── yellow.png           # Yellow signal image
│   └── green.png            # Green signal image
├── up/                      # Vehicles moving up (car.png, bus.png, etc.)
├── down/                    # Vehicles moving down
├── left/                    # Vehicles moving left
└── right/                   # Vehicles moving right
```

## �🎯 Overview

This manual simulation (`manual_simulation.py`) was created specifically to be controlled from the dashboard's manual control interface. It provides a clean, responsive traffic simulation that prioritizes real-time dashboard control over complex traffic management algorithms.

## 🚀 Quick Start

### Option 1: Complete System (Dashboard + Simulation)
```bash
# Terminal 1: Start Backend
cd /Users/syedasif/final-final/dashboard/backend
/Users/syedasif/final-final/.venv/bin/python app.py

# Terminal 2: Start Frontend  
cd /Users/syedasif/final-final/dashboard
npm start

# Terminal 3: Start Manual Simulation
cd /Users/syedasif/final-final
/Users/syedasif/final-final/.venv/bin/python simulation/manual_simulation.py
```

### Option 2: Standalone Simulation (Testing)
```bash
cd /Users/syedasif/final-final
/Users/syedasif/final-final/.venv/bin/python simulation/launch_manual_simulation.py
```

## 🎮 Controls

### Dashboard Controls (Recommended)
1. Open dashboard at http://localhost:3001
2. Navigate to "Manual Control" in the sidebar
3. Toggle "Manual Mode" ON
4. Use Red/Yellow/Green buttons for each direction:
   - **North** (Signal 0): Controls traffic from bottom to top
   - **East** (Signal 1): Controls traffic from left to right  
   - **South** (Signal 2): Controls traffic from top to bottom
   - **West** (Signal 3): Controls traffic from right to left

### Keyboard Controls (Testing)
- **1-4**: Cycle signals for North/East/South/West
- **Space**: Spawn a new vehicle
- **ESC/Close Window**: Exit simulation

## 🚗 Features

### Visual Experience
- **🎨 Realistic Graphics**: Actual vehicle images and traffic signal graphics
- **🛣️ Authentic Roads**: Intersection background with proper lane markings
- **📱 Responsive Design**: Smooth 60 FPS animation with high-quality sprites
- **🔄 Fallback Support**: Graceful degradation to colored shapes if images unavailable

### Vehicle System
- **6 Vehicle Types**: car, bus, truck, bike, rickshaw, ambulance (updated!)
- **Multi-lane Traffic**: 2 lanes per direction
- **Realistic Movement**: Vehicles stop at red lights, follow each other
- **Indian Vehicle Support**: Includes auto-rickshaws and varied speeds
- **Direction-based Sprites**: Different vehicle orientations for each direction

### Traffic Signals  
- **4-Direction Control**: North, East, South, West intersections
- **Real-time Response**: Immediate response to dashboard commands
- **Authentic Signal Images**: Actual red, yellow, green traffic light images
- **State Synchronization**: Dashboard shows current signal states

### Dashboard Integration
- **Socket.IO Communication**: Real-time bidirectional communication
- **Manual Mode Override**: Disable automatic timing when manual mode is on
- **Signal State Broadcasting**: Live updates to dashboard
- **Connection Status**: Visual feedback of connection state

## 🏗️ Architecture

### Core Components

#### `ManualSimulation` Class
- Main simulation manager
- Handles pygame initialization and main loop
- Manages vehicles and traffic signals
- Coordinates dashboard communication

#### `Vehicle` Class  
- Individual vehicle behavior
- Traffic signal response
- Lane following and collision avoidance
- Intersection crossing detection

#### `TrafficSignal` Class
- Signal state management (red/yellow/green)
- Visual rendering
- State change logging

#### `ManualControlClient` Class
- Socket.IO client for dashboard communication
- Event handling for manual control commands
- Signal state broadcasting

### Communication Flow
```
Dashboard Manual Control → Backend Socket.IO → Simulation Socket.IO → Traffic Signals → Vehicle Behavior
```

## 🔧 Configuration

### Simulation Parameters
```python
# Vehicle spawn rate (frames between spawns)
spawn_interval = 120  # 2 seconds at 60 FPS

# Vehicle types and speeds
VEHICLE_SPEEDS = {
    "car": 2.5,
    "bus": 2.0, 
    "truck": 1.8,
    "bike": 3.0,
    "auto-rickshaw": 2.2
}

# Intersection layout
INTERSECTION_CENTER_X = 700
INTERSECTION_CENTER_Y = 400
INTERSECTION_SIZE = 120
```

### Backend Integration
```python
# Dashboard backend URL
BACKEND_URL = 'http://localhost:5050'

# Socket.IO events
- 'simulation_manual_signal': Receive signal changes
- 'simulation_manual_mode': Receive mode toggle
- 'signal_state_update': Send current signal states
```

## 🎨 Visual Design

### Traffic Intersection
- **Realistic Layout**: 4-way intersection with proper lane markings
- **Stop Lines**: Clear visual boundaries for signal compliance
- **Lane Markings**: Yellow dashed lines for lane separation
- **Signal Placement**: Positioned at realistic intersection corners

### Vehicle Rendering
- **Color-coded Types**: Different colors for each vehicle type
- **Direction Indicators**: White arrows showing movement direction
- **State Visualization**: Darker colors when stopped
- **Size Variation**: Appropriate sizes for different vehicle types

### User Interface
- **Connection Status**: Real-time dashboard connection indicator
- **Manual Mode Display**: Clear indication when manual mode is active
- **Statistics Panel**: Vehicle counts and simulation metrics
- **Instructions**: Built-in help for keyboard controls

## 🔍 Debugging

### Common Issues

#### Dashboard Connection Failed
```bash
# Check if backend is running
curl http://localhost:5050/api/traffic-data

# Check backend logs for Socket.IO connections
# Look for: "Manual simulation connected to dashboard"
```

#### Signal Commands Not Working
1. Verify manual mode is enabled in dashboard
2. Check browser console for Socket.IO errors
3. Confirm signal IDs match ('0', '1', '2', '3')

#### Vehicles Not Responding
1. Check signal states in simulation UI
2. Verify vehicle spawning (Space key)
3. Check intersection coordinates in console

### Debug Mode
Add debug prints to see signal changes:
```python
# In ManualControlClient.on_manual_signal()
print(f"🚦 Received: Signal {signal_id} -> {new_state}")

# In TrafficSignal.set_state()  
print(f"🚦 Changed: {DIRECTION_NAMES[self.direction]} -> {new_state}")
```

## 📈 Performance

### Optimization
- **60 FPS**: Smooth animation and responsive controls
- **Efficient Rendering**: Minimal pygame draw calls
- **Smart Updates**: Only update changed elements
- **Memory Management**: Remove off-screen vehicles

### Scalability
- **Configurable Spawn Rate**: Adjust traffic density
- **Lane Expansion**: Easy to add more lanes
- **Vehicle Type Extension**: Simple to add new vehicle types
- **Signal Addition**: Framework supports more intersections

## 🔮 Future Enhancements

### Planned Features
1. **Multiple Intersections**: Network of connected intersections
2. **Emergency Vehicle Priority**: Ambulance/fire truck preemption
3. **Traffic Statistics**: Real-time analytics and reporting
4. **Route Planning**: Vehicles with specific destinations
5. **Rush Hour Simulation**: Time-based traffic patterns

### Integration Opportunities
1. **Real CCTV Integration**: Use actual traffic camera feeds
2. **IoT Sensor Data**: Real vehicle detection input
3. **Machine Learning**: AI-powered traffic optimization
4. **Mobile App**: Remote traffic control interface
5. **Cloud Deployment**: Multi-city traffic management

## 🎯 Usage Examples

### Basic Manual Control
```python
# Start simulation programmatically
from manual_simulation import ManualSimulation

sim = ManualSimulation()
sim.set_signal_state(0, 'green')  # North to green
sim.set_signal_state(1, 'red')    # East to red
sim.run()  # Start main loop
```

### Emergency Mode
```python
# Quick emergency clearing (all signals to red)
for direction in [0, 1, 2, 3]:
    sim.set_signal_state(direction, 'red')
    
# Then allow emergency vehicle direction
sim.set_signal_state(emergency_direction, 'green')
```

### Traffic Statistics
```python
# Get real-time statistics
stats = {
    'active_vehicles': len(sim.vehicles),
    'spawned_total': sim.vehicles_spawned,
    'completed_total': sim.vehicles_completed,
    'signal_states': sim.get_signal_states()
}
```

---

## 🤝 Integration with Existing System

This manual simulation is designed to work alongside the existing `simulation.py` but with a focus on dashboard control. Key differences:

- **Simplified Logic**: Prioritizes responsiveness over complex traffic algorithms
- **Dashboard-First**: Built specifically for manual control interface
- **Real-time Updates**: Immediate response to dashboard commands  
- **Visual Clarity**: Clear, modern interface design
- **Testing-Friendly**: Easy to test individual components

The simulation maintains the same Socket.IO interface as the original, making it a drop-in replacement for manual control scenarios.