# 🚦 Smart Traffic Dashboard - Backend API

Flask-based REST API and WebSocket server for the Smart Traffic Management Dashboard.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip (Python package installer)

### Installation
```bash
cd backend
pip install -r requirements.txt
python run.py
```

The server will start on `http://localhost:5000`

## 📡 API Endpoints

### Traffic Statistics
```http
GET /api/stats
```
Returns current traffic statistics including vehicle counts, CO₂ savings, and wait times.

**Response:**
```json
{
  "vehicles_detected": 245,
  "co2_saved": 156,
  "avg_wait_time": 12.3,
  "mode": "automation",
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

### Traffic Alerts
```http
GET /api/alerts
```
Returns current traffic alerts and notifications.

**Response:**
```json
{
  "alerts": [
    {
      "id": 1,
      "type": "accident",
      "message": "Minor accident reported at Main St & 1st Ave",
      "timestamp": "2024-01-15T10:30:00.000Z",
      "severity": "medium",
      "location": "Main St & 1st Ave"
    }
  ],
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

### Map Data
```http
GET /api/map-data
```
Returns traffic signals and emergency vehicle locations.

**Response:**
```json
{
  "signals": [
    {
      "id": 1,
      "name": "Main St & 1st Ave",
      "lat": 40.7128,
      "lng": -74.0060,
      "vehicles_detected": 25,
      "co2_level": 95,
      "camera_feed_url": "https://example.com/camera1",
      "status": "active",
      "queue_length": 8
    }
  ],
  "emergency_vehicles": [
    {
      "id": "AMB-001",
      "type": "ambulance",
      "lat": 40.7505,
      "lng": -73.9934,
      "status": "en_route",
      "destination": "5th Ave & 34th St",
      "eta": "3 mins"
    }
  ],
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

### Analytics Data
```http
GET /api/analytics
```
Returns historical traffic data and trends.

**Response:**
```json
{
  "hourly_traffic": [
    {
      "hour": 10,
      "vehicles": 45,
      "co2_saved": 12
    }
  ],
  "co2_trends": [
    {
      "date": "2024-01-15",
      "co2_saved": 156
    }
  ],
  "congestion_hotspots": [
    {
      "location": "Broadway & 42nd St",
      "congestion_level": 85,
      "trend": "increasing"
    }
  ],
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

### Mode Toggle
```http
POST /api/mode
Content-Type: application/json

{
  "mode": "manual"
}
```
Toggle between automation and manual control modes.

**Response:**
```json
{
  "success": true,
  "mode": "manual"
}
```

### Camera Feed
```http
GET /api/signal/<signal_id>/camera
```
Get camera feed information for a specific traffic signal.

**Response:**
```json
{
  "camera_url": "https://example.com/camera1",
  "signal_info": {
    "id": 1,
    "name": "Main St & 1st Ave",
    "lat": 40.7128,
    "lng": -74.0060,
    "vehicles_detected": 25,
    "co2_level": 95,
    "camera_feed_url": "https://example.com/camera1",
    "status": "active",
    "queue_length": 8
  }
}
```

## 🔌 WebSocket Events

### Connection
```javascript
const socket = io('http://localhost:5000');

socket.on('connect', () => {
  console.log('Connected to server');
  socket.emit('subscribe_to_updates');
});
```

### Real-time Updates

#### Statistics Updates
```javascript
socket.on('stats_update', (data) => {
  console.log('Stats updated:', data);
  // data: { vehicles_detected, co2_saved, avg_wait_time, timestamp }
});
```

#### Signal Updates
```javascript
socket.on('signals_update', (data) => {
  console.log('Signals updated:', data);
  // data: { signals: [...], timestamp }
});
```

#### New Alerts
```javascript
socket.on('new_alert', (alert) => {
  console.log('New alert:', alert);
  // alert: { id, type, message, timestamp, severity, location }
});
```

#### Mode Changes
```javascript
socket.on('mode_changed', (data) => {
  console.log('Mode changed:', data.mode);
  // data: { mode: 'automation' | 'manual' }
});
```

## 🏗️ Architecture

### File Structure
```
backend/
├── app.py              # Main Flask application
├── run.py              # Server startup script
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

### Key Components

#### Flask Application (`app.py`)
- REST API endpoints
- WebSocket event handlers
- Mock data generation
- Background update tasks

#### Mock Data System
- Realistic traffic signal data
- Simulated vehicle movements
- Dynamic alert generation
- Emergency vehicle tracking

#### Background Tasks
- Real-time data updates every 5 seconds
- Automatic alert generation
- Statistics calculation
- Emergency vehicle simulation

## 🔧 Configuration

### Environment Variables
```bash
export FLASK_ENV=development
export FLASK_DEBUG=1
export SECRET_KEY=your-secret-key-here
```

### CORS Settings
The API is configured to accept requests from `http://localhost:3000` (React dev server).

### WebSocket Configuration
- Transport: WebSocket
- CORS: Enabled for localhost:3000
- Auto-reconnect: Enabled

## 🧪 Testing

### Manual Testing
```bash
# Test stats endpoint
curl http://localhost:5000/api/stats

# Test alerts endpoint
curl http://localhost:5000/api/alerts

# Test mode toggle
curl -X POST http://localhost:5000/api/mode \
  -H "Content-Type: application/json" \
  -d '{"mode": "manual"}'
```

### WebSocket Testing
Use a WebSocket client like `wscat`:
```bash
npm install -g wscat
wscat -c ws://localhost:5000
```

## 🚀 Production Deployment

### Using Gunicorn
```bash
pip install gunicorn
gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:5000 app:app
```

### Using Docker
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["python", "run.py"]
```

### Environment Configuration
```bash
export FLASK_ENV=production
export FLASK_DEBUG=0
export SECRET_KEY=your-production-secret-key
```

## 🔒 Security Considerations

- CORS configuration for allowed origins
- Input validation on API endpoints
- Rate limiting (implement as needed)
- Secure WebSocket connections
- Environment variable protection

## 📊 Monitoring

### Logs
The application logs:
- WebSocket connections/disconnections
- API endpoint access
- Background task execution
- Error conditions

### Health Check
```http
GET /api/health
```
Returns server status and basic metrics.

## 🛠️ Development

### Adding New Endpoints
1. Define route in `app.py`
2. Add error handling
3. Update documentation
4. Test with frontend

### Adding WebSocket Events
1. Define event handler in `app.py`
2. Update frontend socket listeners
3. Test real-time updates

### Mock Data Customization
Modify the `initialize_mock_data()` function to:
- Add more traffic signals
- Change signal locations
- Adjust update frequencies
- Customize alert types

## 🐛 Troubleshooting

### Common Issues

#### Port Already in Use
```bash
# Find process using port 5000
lsof -i :5000
# Kill the process
kill -9 <PID>
```

#### WebSocket Connection Failed
- Check CORS settings
- Verify firewall configuration
- Ensure both servers are running

#### Module Import Errors
```bash
# Reinstall dependencies
pip install -r requirements.txt
```

## 📈 Performance Optimization

- Use connection pooling for database connections
- Implement caching for frequently accessed data
- Optimize background task frequencies
- Add rate limiting for API endpoints
- Monitor memory usage and WebSocket connections

---

For more information, see the main project README.md file.
