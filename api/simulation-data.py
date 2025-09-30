from flask import Flask, jsonify, request
import random
import time

app = Flask(__name__)

# Global simulation data cache
simulation_data_cache = {
    'vehicles_detected': 127,
    'last_update': 0
}

def handler(event, context):
    """Vercel serverless function handler for simulation data"""
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
    
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization'
        },
        'body': simulation_data
    }