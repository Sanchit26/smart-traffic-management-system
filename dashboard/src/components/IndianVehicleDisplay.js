import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

const IndianVehicleDisplay = () => {
  const [vehicleData, setVehicleData] = useState(null);
  const [dataSource, setDataSource] = useState('cv'); // 'simulation' or 'cv'
  const [loading, setLoading] = useState(true);
  const [lastUpdated, setLastUpdated] = useState(null);

  useEffect(() => {
    const fetchVehicleData = async () => {
      try {
        setLoading(true);
        const endpoint = dataSource === 'simulation' 
          ? '/api/simulation-data' 
          : '/api/cv-vehicle-data';
        
        const response = await fetch(`http://localhost:5050${endpoint}`);
        const data = await response.json();
        
        setVehicleData(data);
        setLastUpdated(new Date().toLocaleTimeString());
      } catch (error) {
        console.error('Error fetching vehicle data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchVehicleData();
    const interval = setInterval(fetchVehicleData, 2000); // Update every 2 seconds

    return () => clearInterval(interval);
  }, [dataSource]);

  const renderIndianVehicleBreakdown = (breakdown) => {
    if (!breakdown) return null;
    
    // Enhanced colors and icons for Indian vehicles
    const vehicleConfig = {
      car: { color: '#10B981', icon: '🚗', label: 'Cars' },
      motorcycle: { color: '#3B82F6', icon: '🏍️', label: 'Motorcycles' },
      auto_rickshaw: { color: '#F59E0B', icon: '🛺', label: 'Auto-Rickshaws', special: true },
      bus: { color: '#EF4444', icon: '🚌', label: 'Buses' },
      truck: { color: '#8B5CF6', icon: '🚚', label: 'Trucks' },
      tempo: { color: '#F97316', icon: '🚐', label: 'Tempo', special: true },
      bicycle: { color: '#06B6D4', icon: '🚲', label: 'Bicycles' },
      person: { color: '#EC4899', icon: '🚶', label: 'Pedestrians' }
    };

    return (
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {Object.entries(breakdown).map(([type, count]) => {
          if (count === 0) return null;
          
          const config = vehicleConfig[type] || { color: '#6B7280', icon: '🚗', label: type };
          
          return (
            <motion.div
              key={type}
              initial={{ scale: 0, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ duration: 0.3 }}
              className={`relative p-4 rounded-xl text-white text-center transform transition-all duration-200 hover:scale-105 cursor-pointer ${
                config.special ? 'ring-2 ring-yellow-400 shadow-lg' : ''
              }`}
              style={{ 
                background: config.special 
                  ? `linear-gradient(135deg, ${config.color}, #F59E0B)` 
                  : config.color,
                boxShadow: config.special ? '0 8px 25px rgba(245, 158, 11, 0.3)' : '0 4px 15px rgba(0,0,0,0.1)'
              }}
            >
              {config.special && (
                <div className="absolute -top-2 -right-2 bg-yellow-500 text-black text-xs px-2 py-1 rounded-full font-bold">
                  🇮🇳
                </div>
              )}
              
              <div className="text-3xl mb-2">{config.icon}</div>
              <div className="text-2xl font-bold mb-1">{count}</div>
              <div className="text-sm opacity-90 font-medium">{config.label}</div>
              
              {config.special && (
                <div className="text-xs mt-1 bg-black bg-opacity-20 rounded px-2 py-1">
                  Indian Specific
                </div>
              )}
            </motion.div>
          );
        })}
      </div>
    );
  };

  const renderEmergencyAlerts = (alerts) => {
    if (!alerts || alerts.length === 0) return null;

    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mt-6"
      >
        <h3 className="text-lg font-semibold text-gray-800 mb-3 flex items-center">
          🚨 Traffic Alerts
          <span className="ml-2 bg-red-100 text-red-800 text-xs px-2 py-1 rounded-full">
            {alerts.length}
          </span>
        </h3>
        <div className="space-y-3">
          {alerts.map((alert, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
              className={`p-4 rounded-lg border-l-4 ${
                alert.severity === 'high' ? 'bg-red-50 border-red-500 text-red-800' :
                alert.severity === 'medium' ? 'bg-yellow-50 border-yellow-500 text-yellow-800' :
                'bg-blue-50 border-blue-500 text-blue-800'
              }`}
            >
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  <div className="font-medium">{alert.message}</div>
                  <div className="text-sm opacity-75 mt-1">
                    {alert.type?.replace(/_/g, ' ')} • Severity: {alert.severity}
                  </div>
                </div>
                <div className="text-xs opacity-60 ml-4">
                  {new Date(alert.timestamp).toLocaleTimeString()}
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </motion.div>
    );
  };

  if (loading && !vehicleData) {
    return (
      <div className="bg-white rounded-xl shadow-lg p-6">
        <div className="animate-pulse">
          <div className="h-6 bg-gray-200 rounded mb-4"></div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {[1,2,3,4].map(i => (
              <div key={i} className="h-20 bg-gray-200 rounded-xl"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-gradient-to-br from-white to-gray-50 rounded-2xl shadow-xl p-8 border border-gray-100">
      {/* Header */}
      <div className="flex justify-between items-center mb-8">
        <h2 className="text-3xl font-bold text-gray-800 flex items-center">
          🇮🇳 Indian Traffic Detection System
          {vehicleData?.detection_type === 'indian_traffic_enhanced' && (
            <span className="ml-4 bg-gradient-to-r from-orange-500 to-red-500 text-white text-sm px-4 py-2 rounded-full shadow-lg">
              ⚡ Enhanced AI Model
            </span>
          )}
        </h2>
        
        <div className="flex space-x-3">
          <button
            onClick={() => setDataSource('simulation')}
            className={`px-6 py-3 rounded-xl font-semibold transition-all duration-300 transform hover:scale-105 ${
              dataSource === 'simulation'
                ? 'bg-blue-500 text-white shadow-lg'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            🎮 Simulation
          </button>
          <button
            onClick={() => setDataSource('cv')}
            className={`px-6 py-3 rounded-xl font-semibold transition-all duration-300 transform hover:scale-105 ${
              dataSource === 'cv'
                ? 'bg-green-500 text-white shadow-lg'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            📹 Live CCTV
          </button>
        </div>
      </div>

      {/* Status Bar */}
      <div className="flex flex-wrap gap-6 mb-8 p-6 bg-gradient-to-r from-gray-50 to-blue-50 rounded-xl border">
        <div className="flex items-center space-x-3">
          <div className={`w-4 h-4 rounded-full ${
            vehicleData?.cv_active || vehicleData?.simulation_active ? 'bg-green-500 animate-pulse shadow-lg' : 'bg-red-500'
          }`}></div>
          <span className="text-sm font-medium text-gray-700">
            {dataSource === 'cv' ? '📹 CV Module' : '🎮 Simulation'} Status
          </span>
        </div>
        
        {vehicleData?.model && (
          <div className="flex items-center space-x-3">
            <span className="text-sm font-medium text-gray-700">
              🤖 AI Model: <span className="font-mono text-blue-600 bg-blue-100 px-3 py-1 rounded-lg">
                {vehicleData.model}
              </span>
            </span>
          </div>
        )}
        
        {lastUpdated && (
          <div className="flex items-center space-x-3">
            <span className="text-sm font-medium text-gray-700">
              ⏰ Last Update: <span className="font-mono bg-gray-100 px-2 py-1 rounded">{lastUpdated}</span>
            </span>
          </div>
        )}
      </div>

      {/* Total Count with Traffic Density */}
      <motion.div
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        className="bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 text-white p-8 rounded-2xl mb-8 shadow-xl"
      >
        <div className="text-center">
          <motion.div
            key={vehicleData?.vehicles_detected || vehicleData?.total_vehicles || 0}
            initial={{ scale: 1.2 }}
            animate={{ scale: 1 }}
            className="text-5xl font-bold mb-3"
          >
            {vehicleData?.vehicles_detected || vehicleData?.total_vehicles || 0}
          </motion.div>
          <div className="text-2xl opacity-90 mb-3">Total Vehicles Detected</div>
          
          {vehicleData?.traffic_density && (
            <div className="inline-flex items-center bg-white bg-opacity-25 rounded-full px-6 py-3">
              <span className="text-lg font-semibold">
                🚦 Traffic Density: 
                <span className={`ml-3 font-bold ${
                  vehicleData.traffic_density === 'high' ? 'text-red-200' :
                  vehicleData.traffic_density === 'medium' ? 'text-yellow-200' :
                  'text-green-200'
                }`}>
                  {vehicleData.traffic_density.toUpperCase()}
                </span>
              </span>
            </div>
          )}
        </div>
      </motion.div>

      {/* Vehicle Breakdown */}
      {vehicleData?.vehicle_breakdown && (
        <div className="mb-8">
          <h3 className="text-xl font-bold text-gray-800 mb-6 flex items-center">
            🚗 Vehicle Breakdown Analysis
            <span className="ml-3 bg-blue-100 text-blue-800 text-sm px-3 py-1 rounded-full">
              🔬 AI Enhanced Detection
            </span>
          </h3>
          {renderIndianVehicleBreakdown(vehicleData.vehicle_breakdown)}
        </div>
      )}

      {/* Indian Specific Vehicles Highlight */}
      {vehicleData?.indian_specific_vehicles && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-6 p-4 bg-gradient-to-r from-orange-100 to-yellow-100 rounded-xl border-2 border-orange-200"
        >
          <h3 className="text-lg font-semibold text-orange-800 mb-3 flex items-center">
            🇮🇳 Indian Road Specific Vehicles
            <span className="ml-2 bg-orange-200 text-orange-800 text-xs px-2 py-1 rounded-full">
              Specialized Detection
            </span>
          </h3>
          <div className="grid grid-cols-2 gap-4">
            {Object.entries(vehicleData.indian_specific_vehicles).map(([type, count]) => (
              <div key={type} className="text-center bg-white rounded-lg p-3 shadow-sm">
                <div className="text-2xl font-bold text-orange-600 mb-1">{count}</div>
                <div className="text-sm text-orange-700 capitalize font-medium">
                  {type.replace('_', ' ')}
                </div>
              </div>
            ))}
          </div>
        </motion.div>
      )}

      {/* Lane Distribution */}
      {vehicleData?.lane_counts && Object.keys(vehicleData.lane_counts).length > 0 && (
        <div className="mb-6">
          <h3 className="text-lg font-semibold text-gray-800 mb-3">🛣️ Lane Distribution</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {Object.entries(vehicleData.lane_counts).map(([lane, count]) => (
              <motion.div
                key={lane}
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                className="bg-gradient-to-br from-gray-100 to-gray-200 p-4 rounded-lg text-center shadow-sm hover:shadow-md transition-shadow"
              >
                <div className="text-xl font-bold text-gray-800">{count}</div>
                <div className="text-sm text-gray-600 capitalize font-medium">
                  {lane.replace('_', ' ')}
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      )}

      {/* Emergency Alerts */}
      {renderEmergencyAlerts(vehicleData?.emergency_alerts)}

      {/* Detection Info */}
      {vehicleData?.detection_confidence && (
        <div className="mt-6 p-4 bg-gray-50 rounded-lg">
          <div className="flex justify-center items-center space-x-6 text-sm text-gray-600">
            <div>
              Detection Confidence: 
              <span className="font-bold ml-1 text-green-600">
                {(vehicleData.detection_confidence * 100).toFixed(1)}%
              </span>
            </div>
            {vehicleData.frame_number && (
              <div>
                Frame: <span className="font-mono font-bold">{vehicleData.frame_number}</span>
              </div>
            )}
            {vehicleData.timestamp && (
              <div>
                Last Detection: 
                <span className="font-mono ml-1">
                  {new Date(vehicleData.timestamp).toLocaleTimeString()}
                </span>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default IndianVehicleDisplay;