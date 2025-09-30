from flask import Flask, jsonify, request
from flask_cors import CORS
import random
import time
import json
from datetime import datetime, timedelta
import os

app = Flask(__name__)
CORS(app, origins=["*"])

# Initialize data structures
traffic_data = {
    'signals': [],
    'vehicles_detected': 0,
    'co2_saved': 0,
    'avg_wait_time': 0,
    'emergency_vehicles': []
}

signals_vehicle_data = {"signals_vehicle_data": [], "system_totals": {"total_vehicles_detected": 0}}

# Global simulation data to maintain consistency
simulation_data_cache = {
    'vehicles_detected': 127,
    'last_update': 0
}

# Initialize mock data
def initialize_mock_data():
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
            'co2_level': random.randint(90, 140),
            'camera_feed_url': 'https://example.com/camera2',
            'status': 'active',
            'queue_length': random.randint(8, 25)
        },
        {
            'id': 3,
            'name': '5th Ave & 59th St',
            'lat': 40.7505,
            'lng': -73.9934,
            'vehicles_detected': random.randint(10, 35),
            'co2_level': random.randint(70, 110),
            'camera_feed_url': 'https://example.com/camera3',
            'status': 'active',
            'queue_length': random.randint(3, 15)
        },
        {
            'id': 4,
            'name': 'Park Ave & 42nd St',
            'lat': 40.7505,
            'lng': -73.9780,
            'vehicles_detected': random.randint(25, 55),
            'co2_level': random.randint(95, 135),
            'camera_feed_url': 'https://example.com/camera4',
            'status': 'active',
            'queue_length': random.randint(10, 30)
        },
        {
            'id': 5,
            'name': 'Madison Ave & 57th St',
            'lat': 40.7614,
            'lng': -73.9776,
            'vehicles_detected': random.randint(18, 40),
            'co2_level': random.randint(85, 125),
            'camera_feed_url': 'https://example.com/camera5',
            'status': 'active',
            'queue_length': random.randint(6, 22)
        }
    ]

# Initialize data
initialize_mock_data()

def calculate_stats():
    """Calculate overall statistics"""
    total_vehicles = sum(signal['vehicles_detected'] for signal in traffic_data['signals'])
    traffic_data['vehicles_detected'] = max(0, total_vehicles)
    traffic_data['co2_saved'] = random.randint(1200, 2500)
    traffic_data['avg_wait_time'] = random.uniform(45, 120)

# API Routes
@app.route('/api/signals-vehicle-data', methods=['GET'])
def get_signals_vehicle_data():
    """Get detailed vehicle counts for all signals"""
    calculate_stats()
    
    enhanced_data = {
        'signals_vehicle_data': traffic_data['signals'],
        'system_totals': {
            'total_vehicles_detected': traffic_data['vehicles_detected'],
            'avg_wait_time': traffic_data['avg_wait_time'],
            'co2_saved': traffic_data['co2_saved']
        }
    }
    
    return jsonify(enhanced_data)

@app.route('/api/simulation-data', methods=['GET'])
def get_simulation_data():
    """Get vehicle data specifically from simulation"""
    global simulation_data_cache
    current_time = time.time()
    
    # Update vehicle count slowly (every 30 seconds)
    if current_time - simulation_data_cache['last_update'] > 30:
        change = random.choice([-2, -1, 0, 0, 1, 1, 2, 3, 4, 5])
        simulation_data_cache['vehicles_detected'] += change
        simulation_data_cache['vehicles_detected'] = max(80, min(200, simulation_data_cache['vehicles_detected']))
        simulation_data_cache['last_update'] = current_time
    
    simulation_data = {
        'data_source': 'simulation',
        'vehicles_detected': simulation_data_cache['vehicles_detected'],
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
            'signal_1': 'green',
            'signal_2': 'red',
            'signal_3': 'yellow',
            'signal_4': 'red'
        }
    }
    
    return jsonify(simulation_data)

@app.route('/api/cv-vehicle-data', methods=['GET'])
def get_cv_vehicle_data():
    """Get CV (Computer Vision) vehicle data"""
    cv_data = {
        'data_source': 'cv',
        'vehicles_detected': random.randint(50, 120),
        'lane_counts': {
            'lane_1': random.randint(10, 25),
            'lane_2': random.randint(8, 20),
            'lane_3': random.randint(12, 30),
            'lane_4': random.randint(15, 35)
        },
        'vehicle_types': {
            'cars': random.randint(60, 80),
            'trucks': random.randint(5, 15),
            'buses': random.randint(2, 8),
            'motorcycles': random.randint(8, 20),
            'bicycles': random.randint(3, 10)
        }
    }
    
    return jsonify(cv_data)

@app.route('/api/emergency-alerts', methods=['GET'])
def get_emergency_alerts():
    """Get emergency vehicle alerts"""
    alerts = [
        {
            'id': 1,
            'type': 'ambulance',
            'location': 'Main St & 1st Ave',
            'status': 'approaching',
            'eta': '2 minutes',
            'priority': 'high',
            'timestamp': datetime.now().isoformat()
        }
    ]
    
    return jsonify({'alerts': alerts})

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'Smart Traffic Management API'
    })

@app.route('/api/analytics', methods=['GET'])
def get_analytics():
    """Get analytics data for the dashboard"""
    try:
        analytics_data = {
            "total_vehicles": random.randint(150, 300),
            "average_wait_time": round(random.uniform(45, 120), 1),
            "peak_hours": ["8:00-10:00", "17:00-19:00"],
            "efficiency_score": round(random.uniform(75, 95), 1),
            "daily_stats": {
                "processed_vehicles": random.randint(2000, 4000),
                "incidents": random.randint(2, 8),
                "emergency_responses": random.randint(5, 15)
            },
            "hourly_traffic": [
                {"hour": f"{i}:00", "count": random.randint(50, 200)} 
                for i in range(24)
            ]
        }
        return jsonify(analytics_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/map-data', methods=['GET'])
def get_map_data():
    """Get map data including emergency vehicles"""
    try:
        emergency_vehicles = []
        for i in range(random.randint(3, 8)):
            vehicle = {
                "id": f"EMG_{i+1:03d}",
                "type": random.choice(["ambulance", "fire_truck", "police"]),
                "location": {
                    "lat": 20.2961 + random.uniform(-0.01, 0.01),
                    "lng": 85.8245 + random.uniform(-0.01, 0.01)
                },
                "destination": {
                    "lat": 20.2961 + random.uniform(-0.02, 0.02),
                    "lng": 85.8245 + random.uniform(-0.02, 0.02)
                },
                "status": random.choice(["en_route", "arrived", "returning"]),
                "priority": random.choice(["high", "medium", "critical"]),
                "eta": random.randint(5, 30)
            }
            emergency_vehicles.append(vehicle)
        
        map_data = {
            "emergency_vehicles": emergency_vehicles,
            "traffic_density": {
                "north": random.uniform(0.3, 0.9),
                "south": random.uniform(0.3, 0.9),
                "east": random.uniform(0.3, 0.9),
                "west": random.uniform(0.3, 0.9)
            },
            "signal_status": {
                "intersection_1": {"current": "green", "next_change": 45},
                "intersection_2": {"current": "red", "next_change": 23},
                "intersection_3": {"current": "yellow", "next_change": 5}
            }
        }
        return jsonify(map_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/mode', methods=['POST'])
def set_mode():
    """Set the traffic management mode"""
    try:
        data = request.get_json()
        mode = data.get('mode', 'automatic')
        
        # In a real implementation, this would update the system mode
        # For now, just return success
        return jsonify({
            "message": f"Mode set to {mode}",
            "current_mode": mode,
            "timestamp": time.time()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Vercel serverless function handler
def handler(request):
    return app(request.environ, lambda status, headers: None)

if __name__ == '__main__':
    app.run(debug=True)