import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  FiTruck, 
  FiMapPin, 
  FiClock, 
  FiAlertTriangle,
  FiNavigation,
  FiActivity,
  FiUsers,
  FiShield
} from 'react-icons/fi';
import axios from 'axios';

const EmergencyVehicleCard = ({ vehicle, index }) => {
  const getVehicleIcon = (type) => {
    switch (type) {
      case 'ambulance': return '🚑';
      case 'fire_truck': return '🚒';
      case 'police': return '🚔';
      default: return '🚗';
    }
  };

  const getVehicleColor = (type) => {
    switch (type) {
      case 'ambulance': return 'text-red-600 bg-red-50 border-red-200';
      case 'fire_truck': return 'text-red-700 bg-red-50 border-red-200';
      case 'police': return 'text-blue-600 bg-blue-50 border-blue-200';
      default: return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'en_route': return 'text-green-600 bg-green-100';
      case 'stationary': return 'text-yellow-600 bg-yellow-100';
      case 'arrived': return 'text-blue-600 bg-blue-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, delay: index * 0.1 }}
      className={`p-4 rounded-lg border-2 ${getVehicleColor(vehicle.type)} mb-4`}
    >
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center space-x-3">
          <div className="text-2xl">{getVehicleIcon(vehicle.type)}</div>
          <div>
            <h3 className="font-semibold text-gray-800">{vehicle.id}</h3>
            <p className="text-sm text-gray-600 capitalize">
              {vehicle.type.replace('_', ' ')}
            </p>
          </div>
        </div>
        
        <div className="text-right">
          <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(vehicle.status)}`}>
            <FiActivity className="w-3 h-3 mr-1" />
            {vehicle.status.replace('_', ' ')}
          </span>
        </div>
      </div>

      <div className="space-y-2">
        <div className="flex items-center space-x-2 text-sm">
          <FiMapPin className="w-4 h-4 text-gray-500" />
          <span className="text-gray-700">{vehicle.destination}</span>
        </div>
        
        {vehicle.eta !== 'N/A' && (
          <div className="flex items-center space-x-2 text-sm">
            <FiClock className="w-4 h-4 text-gray-500" />
            <span className="text-gray-700">ETA: {vehicle.eta}</span>
          </div>
        )}

        <div className="flex items-center space-x-2 text-sm">
          <FiNavigation className="w-4 h-4 text-gray-500" />
          <span className="text-gray-700">
            Lat: {vehicle.lat.toFixed(4)}, Lng: {vehicle.lng.toFixed(4)}
          </span>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="mt-3">
        <div className="flex justify-between text-xs text-gray-500 mb-1">
          <span>Progress</span>
          <span>{vehicle.status === 'en_route' ? 'In Transit' : 'At Location'}</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div
            className={`h-2 rounded-full ${
              vehicle.status === 'en_route' ? 'bg-blue-500' :
              vehicle.status === 'arrived' ? 'bg-green-500' : 'bg-yellow-500'
            }`}
            style={{
              width: vehicle.status === 'en_route' ? '70%' :
                     vehicle.status === 'arrived' ? '100%' : '30%'
            }}
          ></div>
        </div>
      </div>
    </motion.div>
  );
};

const EmergencyTracking = () => {
  const [emergencyVehicles, setEmergencyVehicles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({
    total_vehicles: 0,
    active_vehicles: 0,
    avg_response_time: '4.2 mins',
    success_rate: '98.5%'
  });

  useEffect(() => {
    fetchEmergencyData();
    const interval = setInterval(fetchEmergencyData, 10000); // Update every 10 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchEmergencyData = async () => {
    try {
      const response = await axios.get('http://localhost:5050/api/map-data', {
        timeout: 10000 // 10 second timeout
      });
      setEmergencyVehicles(response.data.emergency_vehicles || []);
      
      // Calculate stats
      const vehicles = response.data.emergency_vehicles || [];
      const activeVehicles = vehicles.filter(v => v.status === 'en_route').length;
      
      setStats({
        total_vehicles: vehicles.length,
        active_vehicles: activeVehicles,
        avg_response_time: '4.2 mins',
        success_rate: '98.5%'
      });
      
      setLoading(false);
    } catch (error) {
      console.error('Failed to fetch emergency data:', error);
      // Set fallback data
      setEmergencyVehicles([]);
      setStats({
        total_vehicles: 0,
        active_vehicles: 0,
        avg_response_time: 'N/A',
        success_rate: 'N/A'
      });
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-red-500 mx-auto mb-2"></div>
          <p className="text-gray-500">Loading emergency vehicles...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="p-6 border-b border-gray-200">
        <div className="flex items-center space-x-2 mb-4">
          <FiTruck className="w-6 h-6 text-red-500" />
          <h2 className="text-xl font-semibold text-gray-800">Emergency Vehicle Tracking</h2>
        </div>
        
        {/* Stats Grid */}
        <div className="grid grid-cols-2 gap-4">
          <div className="bg-red-50 rounded-lg p-3">
            <div className="flex items-center space-x-2">
              <FiUsers className="w-4 h-4 text-red-500" />
              <span className="text-sm font-medium text-gray-700">Total Vehicles</span>
            </div>
            <div className="text-xl font-bold text-red-600 mt-1">{stats.total_vehicles}</div>
          </div>
          
          <div className="bg-green-50 rounded-lg p-3">
            <div className="flex items-center space-x-2">
              <FiActivity className="w-4 h-4 text-green-500" />
              <span className="text-sm font-medium text-gray-700">Active</span>
            </div>
            <div className="text-xl font-bold text-green-600 mt-1">{stats.active_vehicles}</div>
          </div>
          
          <div className="bg-blue-50 rounded-lg p-3">
            <div className="flex items-center space-x-2">
              <FiClock className="w-4 h-4 text-blue-500" />
              <span className="text-sm font-medium text-gray-700">Avg Response</span>
            </div>
            <div className="text-xl font-bold text-blue-600 mt-1">{stats.avg_response_time}</div>
          </div>
          
          <div className="bg-purple-50 rounded-lg p-3">
            <div className="flex items-center space-x-2">
              <FiShield className="w-4 h-4 text-purple-500" />
              <span className="text-sm font-medium text-gray-700">Success Rate</span>
            </div>
            <div className="text-xl font-bold text-purple-600 mt-1">{stats.success_rate}</div>
          </div>
        </div>
      </div>

      {/* Vehicle List */}
      <div className="flex-1 p-6 overflow-y-auto">
        {emergencyVehicles.length === 0 ? (
          <div className="text-center py-8">
            <FiTruck className="w-12 h-12 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-500">No emergency vehicles currently active</p>
          </div>
        ) : (
          <div>
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-800">Active Vehicles</h3>
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                <span className="text-sm text-gray-600">Live Tracking</span>
              </div>
            </div>
            
            {emergencyVehicles.map((vehicle, index) => (
              <EmergencyVehicleCard key={vehicle.id} vehicle={vehicle} index={index} />
            ))}
          </div>
        )}

        {/* Emergency Response Instructions */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.5 }}
          className="mt-6 bg-yellow-50 border border-yellow-200 rounded-lg p-4"
        >
          <div className="flex items-start space-x-3">
            <FiAlertTriangle className="w-5 h-5 text-yellow-600 mt-0.5" />
            <div>
              <h4 className="font-semibold text-yellow-800 mb-2">Emergency Response Protocol</h4>
              <ul className="text-sm text-yellow-700 space-y-1">
                <li>• All emergency vehicles have priority access to traffic signals</li>
                <li>• Traffic is automatically cleared along emergency routes</li>
                <li>• Real-time coordination with emergency dispatch centers</li>
                <li>• Automatic rerouting of civilian traffic during emergencies</li>
              </ul>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default EmergencyTracking;
