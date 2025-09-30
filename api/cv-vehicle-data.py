from flask import Flask, jsonify
import random

def handler(event, context):
    """Vercel serverless function handler for CV vehicle data"""
    
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
    
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization'
        },
        'body': cv_data
    }