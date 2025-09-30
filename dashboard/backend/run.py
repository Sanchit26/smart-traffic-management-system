#!/usr/bin/env python3
"""
Smart Traffic Management Dashboard - Backend Server
Run this file to start the Flask backend server
"""

import os
import sys
from app import app, socketio

if __name__ == '__main__':
    # Set environment variables
    os.environ['FLASK_ENV'] = 'development'
    os.environ['FLASK_DEBUG'] = '1'
    
    print("🚦 Starting Smart Traffic Management Dashboard Backend...")
    print("📍 Server will be available at: http://localhost:5050")
    print("🔌 WebSocket endpoint: ws://localhost:5050")
    print("📡 API endpoints:")
    print("   - GET  /api/stats")
    print("   - GET  /api/alerts") 
    print("   - GET  /api/map-data")
    print("   - GET  /api/analytics")
    print("   - POST /api/mode")
    print("   - GET  /api/signal/<id>/camera")
    print("\n" + "="*50)
    
    try:
        socketio.run(
            app, 
            debug=True, 
            host='0.0.0.0', 
            port=5050,
            allow_unsafe_werkzeug=True
        )
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Server error: {e}")
        sys.exit(1)
