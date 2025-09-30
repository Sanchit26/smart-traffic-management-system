# Smart Traffic Management System 🚦

A comprehensive traffic management solution with AI-powered analytics and real-time control capabilities, developed for **Government of Odisha** as part of SIH25050.

## 🌟 Features

### 🚦 **Manual Traffic Simulation**
- **Realistic Vehicle Rendering**: Actual PNG images for cars, buses, trucks, bikes, rickshaws, and ambulances
- **4-Way Intersection Control**: Manual signal control from dashboard
- **Real-time Updates**: Socket.IO communication between dashboard and simulation
- **Visual Enhancements**: Traffic signal images and intersection backgrounds

### 🎛️ **Dashboard Interface**
- **Real-time Traffic Monitoring**: Live vehicle counts and signal states
- **Manual Signal Control**: Override automatic signals with manual mode
- **Analytics Panel**: Traffic flow analysis and optimization metrics
- **Emergency Vehicle Tracking**: Priority handling for ambulances and emergency services

### 🔐 **Authentication System**
- **Government Branding**: Official Government of Odisha theme
- **Animated Login**: Traffic-themed interface with moving vehicles
- **Secure Authentication**: Token-based user management
- **Professional Design**: Modern UI with traffic light animations

### 📊 **Realistic Data**
- **Natural Updates**: Vehicle counts change slowly and realistically (every 15-30 seconds)
- **Smart Ranges**: Realistic vehicle count ranges (5-80 per signal)
- **Live Statistics**: Real-time efficiency metrics and traffic flow data

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 16+
- npm/yarn

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/Sanchit26/smart-traffic-management-system.git
cd smart-traffic-management-system
```

2. **Set up Python environment**
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

3. **Set up Dashboard**
```bash
cd dashboard
npm install
cd authlogin
npm install
```

### Running the System

#### **Option 1: Complete System (Recommended)**
```bash
# Terminal 1: Backend
cd dashboard/backend
python app.py

# Terminal 2: Main Dashboard
cd dashboard
npm start

# Terminal 3: Auth Login
cd dashboard/authlogin
DISABLE_ESLINT_PLUGIN=true PORT=3002 npm start

# Terminal 4: Manual Simulation (auto-launches when enabling manual mode)
```

#### **Option 2: Quick Start**
```bash
python run_all.py
```

## 🌐 Access Points

- **Main Dashboard**: http://localhost:3000
- **Authentication**: http://localhost:3002
- **Backend API**: http://localhost:5050
- **Manual Simulation**: Auto-launches when manual mode is enabled

## 🎮 Usage

### **Manual Traffic Control**
1. Open main dashboard at http://localhost:3000
2. Navigate to "Manual Control" in sidebar
3. Toggle **Manual Mode ON**
4. Manual simulation will auto-launch
5. Use Red/Yellow/Green buttons to control traffic signals

### **Authentication**
1. Open http://localhost:3002
2. Experience the traffic-themed login interface
3. Watch realistic live vehicle counter updates

## 🏗️ Architecture

```
📁 smart-traffic-management-system/
├── 🚦 simulation/           # Traffic simulation engine
│   ├── manual_simulation.py # Main manual simulation
│   ├── images/             # Vehicle and signal sprites
│   └── test_*.py          # Testing utilities
├── 🎛️ dashboard/           # Main dashboard interface
│   ├── src/components/    # React components
│   ├── backend/          # Flask API server
│   └── authlogin/        # Authentication system
├── 🤖 ai_module/           # AI traffic detection
├── 🎮 controllers/         # Traffic control algorithms
└── 📊 common/             # Shared utilities
```

## 🔧 Key Components

### **Manual Simulation**
- **Real-time vehicle spawning** with authentic sprites
- **Traffic signal compliance** - vehicles stop at red lights
- **Socket.IO integration** for dashboard control
- **Realistic physics** and movement patterns

### **Dashboard Backend**
- **Flask + Socket.IO** server
- **Realistic data generation** with natural update patterns
- **API endpoints** for traffic data and simulation control
- **Auto-launch** manual simulation on mode toggle

### **Frontend Components**
- **ManualSignalControl**: Real-time traffic signal control
- **TrafficMap**: Interactive map with live data
- **VehicleCountContainer**: Real-time vehicle analytics
- **EmergencyTracking**: Priority vehicle monitoring

## 🎨 Visual Features

### **Realistic Graphics**
- **28 vehicle images** (6 types × 4 directions)
- **Traffic signal sprites** (red, yellow, green)
- **Intersection backgrounds** for authentic roads
- **Smooth animations** at 60 FPS

### **Professional UI**
- **Government of Odisha branding**
- **Traffic light animations** in login
- **Responsive design** with Tailwind CSS
- **Real-time status indicators**

## 📈 Performance

- **Optimized updates**: 15-30 second intervals for realistic feel
- **Efficient rendering**: Pygame with image caching
- **Real-time communication**: Socket.IO with minimal latency
- **Responsive frontend**: React with optimized state management

## 🧪 Testing

```bash
# Test manual simulation
python simulation/test_manual_simulation.py

# Test image loading
python simulation/test_image_validation.py

# Test manual mode auto-launch
python test_manual_mode_launch.py

# Test realistic vehicle counts
python test_realistic_counts.py
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is developed for Government of Odisha as part of Smart India Hackathon 2025 (SIH25050) - Transportation & Logistics.

## 👥 Team

Developed by Team for **Smart India Hackathon 2025**
- **Problem Statement**: SIH25050
- **Domain**: Transportation & Logistics
- **Organization**: Government of Odisha

---

**🚦 Smart Traffic Management System - Making cities smarter, one intersection at a time! 🌟**