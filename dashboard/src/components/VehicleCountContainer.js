import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  FiTruck, 
  FiAlertTriangle, 
  FiActivity, 
  FiEye, 
  FiMonitor,
  FiWifi,
  FiWifiOff
} from 'react-icons/fi';
import { useSocket } from '../context/SocketContext';

const VehicleCountContainer = ({ dataSource = 'auto' }) => {
  const { signalsVehicleData } = useSocket();
  const [vehicleData, setVehicleData] = useState(null);
  const [emergencyAlerts, setEmergencyAlerts] = useState([]);
  const [simulationData, setSimulationData] = useState(null);
  const [cvVehicleData, setCvVehicleData] = useState(null);
  const [isLive, setIsLive] = useState(false);

  // Fetch simulation data
  const fetchSimulationData = async () => {
    try {
      const response = await fetch('http://localhost:5050/api/simulation-data');
      if (response.ok) {
        const data = await response.json();
        setSimulationData(data);
      }
    } catch (error) {
      console.error('Error fetching simulation data:', error);
    }
  };

  // Fetch CV vehicle data
  const fetchCvVehicleData = async () => {
    try {
      const response = await fetch('http://localhost:5050/api/cv-vehicle-data');
      if (response.ok) {
        const data = await response.json();
        setCvVehicleData(data);
      }
    } catch (error) {
      console.error('Error fetching CV vehicle data:', error);
    }
  };

  // Fetch emergency alerts
  const fetchEmergencyAlerts = async () => {
    try {
      const response = await fetch('http://localhost:5050/api/emergency-alerts');
      if (response.ok) {
        const data = await response.json();
        setEmergencyAlerts(data.alerts || []);
      }
    } catch (error) {
      console.error('Error fetching emergency alerts:', error);
    }
  };

  // Determine which data to display
  useEffect(() => {
    const updateVehicleData = () => {
      if (dataSource === 'simulation' && simulationData) {
        setVehicleData({
          total: simulationData.vehicles_detected,
          source: 'Simulation',
          isLive: simulationData.simulation_active,
          details: simulationData.traffic_flow,
          emergency: simulationData.emergency_vehicles || []
        });
        setIsLive(simulationData.simulation_active);
      } else if (dataSource === 'cv' && cvVehicleData) {
        setVehicleData({
          total: cvVehicleData.vehicles_detected,
          source: 'CV Detection',
          isLive: cvVehicleData.cv_active,
          details: cvVehicleData.vehicle_types || {},
          lanes: cvVehicleData.lane_counts || {}
        });
        setIsLive(cvVehicleData.cv_active);
      } else if (dataSource === 'auto') {
        // Auto-detect best data source
        if (cvVehicleData && cvVehicleData.cv_active) {
          setVehicleData({
            total: cvVehicleData.vehicles_detected,
            source: 'CV Detection (Live)',
            isLive: true,
            details: cvVehicleData.vehicle_types || {},
            lanes: cvVehicleData.lane_counts || {}
          });
          setIsLive(true);
        } else if (signalsVehicleData?.system_totals) {
          setVehicleData({
            total: signalsVehicleData.system_totals.total_vehicles_detected,
            source: 'System Data',
            isLive: signalsVehicleData.system_totals.cv_active || false,
            details: {},
            signals: signalsVehicleData.signals_vehicle_data?.length || 0
          });
          setIsLive(signalsVehicleData.system_totals.cv_active || false);
        }
      }
    };

    updateVehicleData();
  }, [dataSource, simulationData, cvVehicleData, signalsVehicleData]);

  // Fetch data periodically
  useEffect(() => {
    const fetchData = () => {
      fetchSimulationData();
      fetchCvVehicleData();
      fetchEmergencyAlerts();
    };

    fetchData();
    const interval = setInterval(fetchData, 3000); // Update every 3 seconds

    return () => clearInterval(interval);
  }, []);

  const getStatusColor = () => {
    if (isLive) return 'text-green-500';
    return 'text-gray-500';
  };

  const getStatusIcon = () => {
    if (isLive) return <FiWifi className="w-4 h-4" />;
    return <FiWifiOff className="w-4 h-4" />;
  };

  const activeEmergencyAlerts = emergencyAlerts.filter(alert => alert.status === 'active');

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-white rounded-xl shadow-lg p-6 border-l-4 border-l-blue-500"
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-blue-50 rounded-lg">
            <FiTruck className="w-6 h-6 text-blue-500" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-gray-900">Vehicle Detection</h3>
            <div className="flex items-center space-x-2 text-sm text-gray-600">
              {getStatusIcon()}
              <span className={getStatusColor()}>
                {vehicleData?.source || 'Loading...'}
              </span>
            </div>
          </div>
        </div>
        
        {/* Data source indicator */}
        <div className="flex items-center space-x-2">
          {dataSource === 'simulation' && <FiMonitor className="w-5 h-5 text-purple-500" />}
          {dataSource === 'cv' && <FiEye className="w-5 h-5 text-green-500" />}
          {dataSource === 'auto' && <FiActivity className="w-5 h-5 text-blue-500" />}
        </div>
      </div>

      {/* Main Vehicle Count */}
      <div className="text-center mb-6">
        <motion.div
          key={vehicleData?.total}
          initial={{ scale: 0.8 }}
          animate={{ scale: 1 }}
          className="text-4xl font-bold text-gray-900 mb-2"
        >
          {vehicleData?.total || 0}
        </motion.div>
        <div className="text-gray-600">Total Vehicles Detected</div>
        {vehicleData?.signals && (
          <div className="text-sm text-gray-500 mt-1">
            Across {vehicleData.signals} signals
          </div>
        )}
      </div>

      {/* Details Section */}
      {vehicleData?.lanes && Object.keys(vehicleData.lanes).length > 0 && (
        <div className="mb-4">
          <h4 className="text-sm font-medium text-gray-700 mb-2">Lane Detection</h4>
          <div className="grid grid-cols-2 gap-2">
            {Object.entries(vehicleData.lanes).map(([lane, count]) => (
              <div key={lane} className="bg-gray-50 p-2 rounded text-center">
                <div className="text-lg font-semibold text-gray-900">{count}</div>
                <div className="text-xs text-gray-600">{lane.replace('_', ' ')}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {vehicleData?.details && typeof vehicleData.details === 'object' && Object.keys(vehicleData.details).length > 0 && (
        <div className="mb-4">
          <h4 className="text-sm font-medium text-gray-700 mb-2">Vehicle Types</h4>
          <div className="space-y-2">
            {Object.entries(vehicleData.details).map(([type, count]) => (
              <div key={type} className="flex justify-between items-center">
                <span className="text-sm text-gray-600 capitalize">{type}</span>
                <span className="text-sm font-medium text-gray-900">{count}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Emergency Alerts */}
      <AnimatePresence>
        {activeEmergencyAlerts.length > 0 && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="border-t pt-4"
          >
            <div className="flex items-center space-x-2 mb-3">
              <FiAlertTriangle className="w-5 h-5 text-red-500" />
              <h4 className="text-sm font-medium text-red-700">Emergency Alerts</h4>
            </div>
            <div className="space-y-2">
              {activeEmergencyAlerts.slice(0, 3).map((alert) => (
                <motion.div
                  key={alert.id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  className="bg-red-50 border border-red-200 rounded-lg p-3"
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="text-sm font-medium text-red-800">
                        {alert.message}
                      </div>
                      <div className="text-xs text-red-600">
                        {alert.location} • {new Date(alert.timestamp).toLocaleTimeString()}
                      </div>
                    </div>
                    <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse"></div>
                  </div>
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Status Footer */}
      <div className="mt-4 pt-3 border-t border-gray-100">
        <div className="flex items-center justify-between text-xs text-gray-500">
          <span>Last updated: {new Date().toLocaleTimeString()}</span>
          <div className="flex items-center space-x-1">
            <div className={`w-2 h-2 rounded-full ${isLive ? 'bg-green-500 animate-pulse' : 'bg-gray-400'}`}></div>
            <span>{isLive ? 'Live' : 'Offline'}</span>
          </div>
        </div>
      </div>
    </motion.div>
  );
};

export default VehicleCountContainer;