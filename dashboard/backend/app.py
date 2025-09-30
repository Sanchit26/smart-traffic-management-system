from flask import Flask, jsonify, request, Response
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import random
import time
import threading
from datetime import datetime, timedelta
import json
import subprocess
import cv2
import numpy as np
import base64
import os
import psutil

app = Flask(__name__)
app.config['SECRET_KEY'] = 'smart-traffic-secret-key'
CORS(app, origins=["http://localhost:3000", "http://localhost:3001"])
socketio = SocketIO(app, cors_allowed_origins=["http://localhost:3000", "http://localhost:3001"], async_mode='threading')

# Global variable to store the latest CV frame
latest_cv_frame = None
cv_data_lock = threading.Lock()

# Load signals vehicle data
signals_vehicle_data = {}
try:
    with open(os.path.join(os.path.dirname(__file__), 'signals_vehicle_data.json'), 'r') as f:
        signals_vehicle_data = json.load(f)
except Exception as e:
    print(f"Warning: Could not load signals_vehicle_data.json: {e}")
    signals_vehicle_data = {"signals_vehicle_data": [], "system_totals": {"total_vehicles_detected": 0}}

# Mock data storage
traffic_data = {
    'vehicles_detected': 0,
    'co2_saved': 0,
    'avg_wait_time': 0,
    'mode': 'automation',  # 'automation' or 'manual'
    'signals': [],
    'alerts': [],
    'emergency_vehicles': [],
    'analytics': {
        'hourly_traffic': [],
        'co2_trends': [],
        'congestion_hotspots': []
    }
}

# Initialize mock data
def initialize_mock_data():
    # Traffic signals data
    traffic_data['signals'] = [
        {
            'id': 1,
            'name': 'Main St & 1st Ave',
            'lat': 40.7128,
            'lng': -74.0060,
            'vehicles_detected': random.randint(15, 45),
            'co2_level': random.randint(80, 120),
            'camera_feed_url': 'https://example.com/camera1',
            'status': 'active',
            'queue_length': random.randint(5, 20)
        },
        {
            'id': 2,
            'name': 'Broadway & 42nd St',
            'lat': 40.7589,
            'lng': -73.9851,
            'vehicles_detected': random.randint(20, 60),
            'co2_level': random.randint(90, 130),
            'camera_feed_url': 'https://example.com/camera2',
            'status': 'active',
            'queue_length': random.randint(8, 25)
        },
        {
            'id': 3,
            'name': '5th Ave & 34th St',
            'lat': 40.7505,
            'lng': -73.9934,
            'vehicles_detected': random.randint(10, 35),
            'co2_level': random.randint(75, 110),
            'camera_feed_url': 'https://example.com/camera3',
            'status': 'active',
            'queue_length': random.randint(3, 15)
        },
        {
            'id': 4,
            'name': 'Park Ave & 57th St',
            'lat': 40.7614,
            'lng': -73.9776,
            'vehicles_detected': random.randint(25, 55),
            'co2_level': random.randint(95, 140),
            'camera_feed_url': 'https://example.com/camera4',
            'status': 'active',
            'queue_length': random.randint(10, 30)
        },
        {
            'id': 5,
            'name': 'Madison Ave & 72nd St',
            'lat': 40.7721,
            'lng': -73.9644,
            'vehicles_detected': random.randint(18, 40),
            'co2_level': random.randint(85, 125),
            'camera_feed_url': 'https://example.com/camera5',
            'status': 'active',
            'queue_length': random.randint(6, 18)
        }
    ]
    
    # Initialize alerts
    traffic_data['alerts'] = [
        {
            'id': 1,
            'type': 'accident',
            'message': 'Minor accident reported at Main St & 1st Ave',
            'timestamp': datetime.now().isoformat(),
            'severity': 'medium',
            'location': 'Main St & 1st Ave'
        },
        {
            'id': 2,
            'type': 'emergency',
            'message': 'Ambulance en route to 5th Ave & 34th St',
            'timestamp': datetime.now().isoformat(),
            'severity': 'high',
            'location': '5th Ave & 34th St'
        }
    ]
    
    # Initialize emergency vehicles
    traffic_data['emergency_vehicles'] = [
        {
            'id': 'AMB-001',
            'type': 'ambulance',
            'lat': 40.7505,
            'lng': -73.9934,
            'status': 'en_route',
            'destination': '5th Ave & 34th St',
            'eta': '3 mins'
        },
        {
            'id': 'FIRE-002',
            'type': 'fire_truck',
            'lat': 40.7589,
            'lng': -73.9851,
            'status': 'stationary',
            'destination': 'Broadway & 42nd St',
            'eta': 'N/A'
        }
    ]
    
    # Initialize analytics data
    now = datetime.now()
    for i in range(24):
        hour = (now - timedelta(hours=i)).hour
        traffic_data['analytics']['hourly_traffic'].append({
            'hour': hour,
            'vehicles': random.randint(20, 80),
            'co2_saved': random.randint(5, 25)
        })
        
    traffic_data['analytics']['co2_trends'] = [
        {'date': (now - timedelta(days=i)).strftime('%Y-%m-%d'), 'co2_saved': random.randint(100, 300)}
        for i in range(7, 0, -1)
    ]
    
    traffic_data['analytics']['congestion_hotspots'] = [
        {'location': 'Broadway & 42nd St', 'congestion_level': 85, 'trend': 'increasing'},
        {'location': '5th Ave & 34th St', 'congestion_level': 72, 'trend': 'stable'},
        {'location': 'Main St & 1st Ave', 'congestion_level': 68, 'trend': 'decreasing'}
    ]

# Calculate aggregate stats
def calculate_stats():
    # Use CV data if available, otherwise use JSON data or mock data
    total_vehicles = 0
    
    # If we have CV frame data, use the lane counts
    if latest_cv_frame and 'lane_counts' in latest_cv_frame:
        lane_counts = latest_cv_frame['lane_counts']
        total_vehicles = sum(lane_counts.values()) if lane_counts else 0
        # Multiply by number of signals to simulate system-wide detection
        total_vehicles = total_vehicles * len(traffic_data['signals'])
    elif signals_vehicle_data and 'system_totals' in signals_vehicle_data:
        # Use data from JSON file
        total_vehicles = signals_vehicle_data['system_totals'].get('total_vehicles_detected', 0)
        # Add some randomization to simulate real-time changes
        total_vehicles += random.randint(-10, 15)
    else:
        # Fallback to existing calculation
        total_vehicles = sum(signal['vehicles_detected'] for signal in traffic_data['signals'])
    
    total_co2_saved = total_vehicles * 0.25  # Estimated CO2 saved per vehicle
    avg_wait = 45 if total_vehicles > 100 else 30 if total_vehicles > 50 else 20
    
    traffic_data['vehicles_detected'] = max(0, total_vehicles)
    traffic_data['co2_saved'] = round(total_co2_saved, 1)
    traffic_data['avg_wait_time'] = avg_wait

# API Endpoints
@app.route('/api/stats', methods=['GET'])
def get_stats():
    calculate_stats()
    return jsonify({
        'vehicles_detected': traffic_data['vehicles_detected'],
        'co2_saved': traffic_data['co2_saved'],
        'avg_wait_time': traffic_data['avg_wait_time'],
        'mode': traffic_data['mode'],
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/alerts', methods=['GET'])
def get_alerts():
    return jsonify({
        'alerts': traffic_data['alerts'],
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/map-data', methods=['GET'])
def get_map_data():
    return jsonify({
        'signals': traffic_data['signals'],
        'emergency_vehicles': traffic_data['emergency_vehicles'],
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/analytics', methods=['GET'])
def get_analytics():
    return jsonify({
        'hourly_traffic': traffic_data['analytics']['hourly_traffic'],
        'co2_trends': traffic_data['analytics']['co2_trends'],
        'congestion_hotspots': traffic_data['analytics']['congestion_hotspots'],
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/mode', methods=['POST'])
def toggle_mode():
    data = request.get_json()
    new_mode = data.get('mode', 'automation')
    
    if new_mode in ['automation', 'manual']:
        traffic_data['mode'] = new_mode
        socketio.emit('mode_changed', {'mode': new_mode})
        return jsonify({'success': True, 'mode': new_mode})
    
    return jsonify({'success': False, 'error': 'Invalid mode'}), 400

@app.route('/api/signal/<int:signal_id>/camera', methods=['GET'])
def get_camera_feed(signal_id):
    signal = next((s for s in traffic_data['signals'] if s['id'] == signal_id), None)
    if signal:
        return jsonify({
            'camera_url': signal['camera_feed_url'],
            'signal_info': signal
        })
    return jsonify({'error': 'Signal not found'}), 404

@app.route('/api/cv-stream')
def cv_video_stream():
    """Stream the latest CV processed video frames"""
    def generate_frames():
        while True:
            with cv_data_lock:
                if latest_cv_frame and 'image' in latest_cv_frame:
                    try:
                        # Decode base64 image
                        img_data = base64.b64decode(latest_cv_frame['image'])
                        # Convert to OpenCV format
                        np_arr = np.frombuffer(img_data, np.uint8)
                        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
                        
                        # Encode frame as JPEG
                        ret, buffer = cv2.imencode('.jpg', frame)
                        if ret:
                            frame_bytes = buffer.tobytes()
                            yield (b'--frame\r\n'
                                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
                    except Exception as e:
                        print(f"Error processing CV frame: {e}")
            time.sleep(0.1)  # 10 FPS
    
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/api/cv-data')
def get_cv_data():
    """Get the latest CV analysis data"""
    with cv_data_lock:
        if latest_cv_frame:
            return jsonify({
                'frame': latest_cv_frame.get('frame', 0),
                'lane_counts': latest_cv_frame.get('lane_counts', {}),
                'timestamp': datetime.now().isoformat()
            })
    return jsonify({'error': 'No CV data available'}), 404

@app.route('/api/signals-vehicle-data', methods=['GET'])
def get_signals_vehicle_data():
    """Get detailed vehicle counts for all signals"""
    # Enhance with real-time CV data if available
    enhanced_data = signals_vehicle_data.copy() if signals_vehicle_data else {"signals_vehicle_data": []}
    
    if latest_cv_frame and 'lane_counts' in latest_cv_frame:
        cv_lane_counts = latest_cv_frame['lane_counts']
        total_cv_vehicles = sum(cv_lane_counts.values()) if cv_lane_counts else 0
        
        # Update system totals with real CV data
        if 'system_totals' not in enhanced_data:
            enhanced_data['system_totals'] = {}
        enhanced_data['system_totals']['total_vehicles_detected'] = total_cv_vehicles * len(traffic_data['signals'])
        enhanced_data['system_totals']['cv_active'] = True
        enhanced_data['system_totals']['last_updated'] = datetime.now().isoformat()
        
        # Update individual signal data with CV data simulation
        if 'signals_vehicle_data' in enhanced_data:
            for i, signal_data in enumerate(enhanced_data['signals_vehicle_data']):
                # Distribute CV counts among signals with some variation
                base_count = total_cv_vehicles // len(enhanced_data['signals_vehicle_data'])
                variation = random.randint(-3, 5)
                signal_data['total_current'] = max(0, base_count + variation + (i * 2))
                signal_data['cv_updated'] = True
    
    return jsonify(enhanced_data)

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'signals_count': len(traffic_data['signals']),
        'alerts_count': len(traffic_data['alerts']),
        'emergency_vehicles_count': len(traffic_data['emergency_vehicles'])
    })

@app.route('/api/start-simulation', methods=['POST'])
def start_simulation():
    import traceback
    try:
        import os
        script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../simulation/simulation.py'))
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
        print(f"[DEBUG] Launching simulation: {script_path} (cwd={project_root})")
        proc = subprocess.Popen(['python3', script_path], cwd=project_root)
        print(f"[DEBUG] Simulation process started with PID: {proc.pid}")
        return jsonify({'status': 'success', 'message': 'Simulation started.'}), 200
    except Exception as e:
        print(f"[ERROR] Failed to start simulation: {e}")
        print(traceback.format_exc())
        return jsonify({'status': 'error', 'message': str(e)}), 500

# === NEW: Separate endpoints for simulation vs CV data ===

# Global simulation data to maintain consistency
simulation_data_cache = {
    'vehicles_detected': 127,
    'last_update': 0
}

@app.route('/api/simulation-data', methods=['GET'])
def get_simulation_data():
    """Get vehicle data specifically from simulation"""
    global simulation_data_cache
    current_time = time.time()
    
    # Update vehicle count slowly (every 30 seconds)
    if current_time - simulation_data_cache['last_update'] > 30:
        # Small realistic changes: -2 to +5 vehicles
        change = random.choice([-2, -1, 0, 0, 1, 1, 2, 3, 4, 5])
        simulation_data_cache['vehicles_detected'] += change
        # Keep in realistic range
        simulation_data_cache['vehicles_detected'] = max(80, min(200, simulation_data_cache['vehicles_detected']))
        simulation_data_cache['last_update'] = current_time
    
    # This will be populated by simulation events
    simulation_data = {
        'data_source': 'simulation',
        'vehicles_detected': simulation_data_cache['vehicles_detected'],  # More stable count
        'emergency_vehicles': [
            {
                'type': 'ambulance',
                'location': 'Main St & 1st Ave',
                'status': 'approaching',
                'eta': '2 minutes',
                'priority': 'high'
            }
        ],
        'signal_states': {
            'signal_1': {'status': 'green', 'time_remaining': 25},
            'signal_2': {'status': 'red', 'time_remaining': 45},
            'signal_3': {'status': 'yellow', 'time_remaining': 3},
            'signal_4': {'status': 'red', 'time_remaining': 18}
        },
        'traffic_flow': {
            'avg_speed': random.randint(15, 35),
            'congestion_level': random.choice(['low', 'medium', 'high']),
            'waiting_time': random.randint(20, 60)
        },
        'timestamp': datetime.now().isoformat(),
        'simulation_active': True
    }
    return jsonify(simulation_data)

@app.route('/api/cv-vehicle-data', methods=['GET'])
def get_cv_vehicle_data():
    """Get enhanced Indian vehicle data from CV module"""
    cv_vehicle_data = {
        'data_source': 'cv_module_indian_enhanced',
        'cv_active': latest_cv_frame is not None,
        'timestamp': datetime.now().isoformat(),
        'model': 'yolov8m_indian_optimized',
        'detection_type': 'indian_traffic_enhanced'
    }
    
    if latest_cv_frame and 'lane_counts' in latest_cv_frame:
        cv_lane_counts = latest_cv_frame['lane_counts']
        total_vehicles = sum(cv_lane_counts.values()) if cv_lane_counts else 0
        
        # Enhanced Indian vehicle breakdown
        indian_vehicle_breakdown = {
            'car': int(total_vehicles * 0.35),           # Cars
            'motorcycle': int(total_vehicles * 0.30),    # Motorcycles/Scooters (very common)
            'auto_rickshaw': int(total_vehicles * 0.15), # Auto-rickshaws (Indian specific)
            'bus': int(total_vehicles * 0.08),           # Buses
            'truck': int(total_vehicles * 0.07),         # Trucks
            'tempo': int(total_vehicles * 0.03),         # Tempo/mini trucks
            'bicycle': int(total_vehicles * 0.02),       # Bicycles
            'person': random.randint(5, 20)              # Pedestrians
        }
        
        cv_vehicle_data.update({
            'vehicles_detected': total_vehicles,
            'lane_counts': cv_lane_counts,
            'frame_number': latest_cv_frame.get('frame', 0),
            'detection_confidence': 0.78,  # Realistic confidence for Indian traffic
            'vehicle_breakdown': indian_vehicle_breakdown,
            'indian_specific_vehicles': {
                'auto_rickshaw': indian_vehicle_breakdown['auto_rickshaw'],
                'tempo': indian_vehicle_breakdown['tempo']
            },
            'traffic_density': 'high' if total_vehicles > 20 else 'medium' if total_vehicles > 10 else 'low'
        })
        
        # Generate Indian traffic specific alerts
        alerts = []
        if indian_vehicle_breakdown['auto_rickshaw'] > 8:
            alerts.append({
                'type': 'HIGH_AUTO_RICKSHAW_DENSITY',
                'message': f"High auto-rickshaw density detected: {indian_vehicle_breakdown['auto_rickshaw']} vehicles",
                'severity': 'medium',
                'timestamp': datetime.now().isoformat()
            })
        
        if indian_vehicle_breakdown['motorcycle'] > 15:
            alerts.append({
                'type': 'HEAVY_MOTORCYCLE_TRAFFIC',
                'message': f"Heavy motorcycle traffic: {indian_vehicle_breakdown['motorcycle']} vehicles",
                'severity': 'low',
                'timestamp': datetime.now().isoformat()
            })
            
        cv_vehicle_data['emergency_alerts'] = alerts
        
    else:
        cv_vehicle_data.update({
            'vehicles_detected': 0,
            'lane_counts': {},
            'frame_number': 0,
            'vehicle_breakdown': {
                'car': 0, 'motorcycle': 0, 'auto_rickshaw': 0, 'bus': 0, 
                'truck': 0, 'tempo': 0, 'bicycle': 0, 'person': 0
            },
            'emergency_alerts': [],
            'error': 'No CV data available'
        })
    
    return jsonify(cv_vehicle_data)

# === NEW: Emergency alert endpoints ===

# Global storage for emergency alerts
emergency_alerts = []
emergency_lock = threading.Lock()

@app.route('/api/emergency-alerts', methods=['GET'])
def get_emergency_alerts():
    """Get current emergency alerts"""
    with emergency_lock:
        return jsonify({
            'alerts': emergency_alerts,
            'total_alerts': len(emergency_alerts),
            'timestamp': datetime.now().isoformat()
        })

@app.route('/simulation/events', methods=['POST'])
def handle_simulation_events():
    """Endpoint to receive events from simulation"""
    try:
        event_data = request.get_json()
        
        # Handle ambulance detection events
        if event_data.get('event') == 'ambulance_detected':
            alert = {
                'id': len(emergency_alerts) + 1,
                'type': 'ambulance',
                'message': f"Ambulance detected in {event_data.get('direction', 'unknown')} direction",
                'location': event_data.get('direction', 'unknown'),
                'timestamp': datetime.now().isoformat(),
                'priority': 'high',
                'status': 'active',
                'source': 'simulation'
            }
            
            with emergency_lock:
                emergency_alerts.append(alert)
                # Keep only last 10 alerts
                if len(emergency_alerts) > 10:
                    emergency_alerts.pop(0)
            
            # Broadcast alert to connected clients
            socketio.emit('emergency_alert', alert, broadcast=True)
            print(f"Emergency alert broadcast: {alert}")
        
        elif event_data.get('event') == 'emergency_cleared':
            # Mark previous alerts as cleared
            with emergency_lock:
                for alert in emergency_alerts:
                    if alert['type'] == 'ambulance' and alert['status'] == 'active':
                        alert['status'] = 'cleared'
                        alert['cleared_at'] = datetime.now().isoformat()
            
            socketio.emit('emergency_cleared', {'message': 'Emergency cleared'}, broadcast=True)
        
        return jsonify({'status': 'success'}), 200
    except Exception as e:
        print(f"Error handling simulation event: {e}")
        return jsonify({'error': str(e)}), 500

# WebSocket Events
@socketio.on('connect')
def handle_connect():
    print('Client connected')
    emit('connected', {'message': 'Connected to traffic management system'})

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('subscribe_to_updates')
def handle_subscribe():
    print('Client subscribed to real-time updates')
    emit('subscription_confirmed', {'message': 'Subscribed to real-time updates'})

@socketio.on('cv_frame')
def handle_cv_frame(data):
    """Handle CV frames from cv_module.py"""
    global latest_cv_frame
    with cv_data_lock:
        latest_cv_frame = data
    # Broadcast the frame to connected dashboard clients
    emit('cv_frame_update', data, broadcast=True)

@socketio.on('manual_signal_change')
def handle_manual_signal_change(data):
    """Handle manual signal changes from dashboard"""
    print(f"📡 Manual signal change: {data}")
    
    # Forward to simulation
    emit('simulation_manual_signal', data, broadcast=True)
    
    # Broadcast to all dashboard clients for real-time updates
    emit('signal_state_update', {
        'signal_id': data['signal_id'],
        'new_state': data['new_state'],
        'timestamp': data['timestamp'],
        'source': 'manual'
    }, broadcast=True)

@socketio.on('manual_mode_toggle')
def handle_manual_mode_toggle(data):
    """Handle manual mode toggle from dashboard"""
    print(f"🎛️ Manual mode toggle: {data}")
    
    manual_mode = data.get('manual_mode', False)
    
    # If manual mode is being enabled, start the manual simulation
    if manual_mode:
        try:
            import os
            script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../simulation/manual_simulation.py'))
            project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
            
            # Check if manual simulation is already running
            import psutil
            manual_sim_running = False
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if proc.info['cmdline'] and 'manual_simulation.py' in ' '.join(proc.info['cmdline']):
                        manual_sim_running = True
                        break
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
            
            if not manual_sim_running:
                print(f"🚀 Launching manual simulation: {script_path}")
                # Use the virtual environment python
                venv_python = os.path.join(project_root, '.venv', 'bin', 'python')
                if os.path.exists(venv_python):
                    proc = subprocess.Popen([venv_python, script_path], cwd=project_root)
                else:
                    proc = subprocess.Popen(['python3', script_path], cwd=project_root)
                print(f"✅ Manual simulation started with PID: {proc.pid}")
                
                # Emit success message
                emit('manual_simulation_status', {
                    'status': 'started',
                    'message': 'Manual simulation launched successfully',
                    'pid': proc.pid
                }, broadcast=True)
            else:
                print("ℹ️ Manual simulation already running")
                emit('manual_simulation_status', {
                    'status': 'already_running',
                    'message': 'Manual simulation is already running'
                }, broadcast=True)
                
        except Exception as e:
            print(f"❌ Failed to start manual simulation: {e}")
            import traceback
            print(traceback.format_exc())
            emit('manual_simulation_status', {
                'status': 'error',
                'message': f'Failed to start manual simulation: {str(e)}'
            }, broadcast=True)
    
    # Forward to simulation
    emit('simulation_manual_mode', data, broadcast=True)
    
    # Broadcast to all dashboard clients
    emit('manual_mode_update', {
        'manual_mode': data['manual_mode'],
        'timestamp': data['timestamp']
    }, broadcast=True)

@socketio.on('signal_state_update')
def handle_signal_state_update(data):
    """Handle signal state updates from simulation and broadcast to dashboard clients"""
    print(f"🚦 Signal state update from simulation: {data}")
    
    # Broadcast to all dashboard clients
    emit('signal_state_update', data, broadcast=True)

# Background task to simulate real-time data updates
def background_updates():
    update_counter = 0
    while True:
        time.sleep(15)  # Update every 15 seconds (slower, more realistic)
        update_counter += 1
        
        # Update traffic signal data - smaller, more realistic changes
        for signal in traffic_data['signals']:
            # Only change vehicle count every few updates (more stability)
            if update_counter % 2 == 0:  # Every 30 seconds
                change = random.choice([-1, -1, 0, 0, 0, 1, 1, 2])  # Bias towards small positive changes
                signal['vehicles_detected'] += change
                signal['vehicles_detected'] = max(5, min(80, signal['vehicles_detected']))  # Keep in realistic range
            
            signal['co2_level'] += random.randint(-1, 2)
            signal['co2_level'] = max(70, min(150, signal['co2_level']))
            signal['queue_length'] += random.randint(-1, 2)
            signal['queue_length'] = max(0, min(25, signal['queue_length']))
        
        # Calculate and emit stats
        calculate_stats()
        socketio.emit('stats_update', {
            'vehicles_detected': traffic_data['vehicles_detected'],
            'co2_saved': traffic_data['co2_saved'],
            'avg_wait_time': traffic_data['avg_wait_time'],
            'timestamp': datetime.now().isoformat()
        })
        
        # Emit signal updates
        socketio.emit('signals_update', {
            'signals': traffic_data['signals'],
            'emergency_vehicles': traffic_data['emergency_vehicles'],
            'timestamp': datetime.now().isoformat()
        })
        
        # Occasionally add new alerts
        if random.random() < 0.1:  # 10% chance every 5 seconds
            alert_types = ['accident', 'emergency', 'congestion', 'maintenance']
            alert_messages = [
                'Traffic congestion detected',
                'Emergency vehicle approaching',
                'Road maintenance in progress',
                'Weather alert: Heavy rain expected'
            ]
            
            new_alert = {
                'id': len(traffic_data['alerts']) + 1,
                'type': random.choice(alert_types),
                'message': random.choice(alert_messages),
                'timestamp': datetime.now().isoformat(),
                'severity': random.choice(['low', 'medium', 'high']),
                'location': random.choice([s['name'] for s in traffic_data['signals']])
            }
            
            traffic_data['alerts'].insert(0, new_alert)
            # Keep only last 20 alerts
            traffic_data['alerts'] = traffic_data['alerts'][:20]
            
            socketio.emit('new_alert', new_alert)

if __name__ == '__main__':
    initialize_mock_data()
    
    # Start background updates in a separate thread
    update_thread = threading.Thread(target=background_updates)
    update_thread.daemon = True
    update_thread.start()
    
    socketio.run(app, debug=True, host='0.0.0.0', port=5050)
