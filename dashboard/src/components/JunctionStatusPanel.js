import React, { useState, useEffect } from 'react';
import { FiZap, FiSettings, FiEye, FiTruck } from 'react-icons/fi';
import { useSocket } from '../context/SocketContext';

const signalColors = {
  red: '#ef4444',
  yellow: '#f59e0b',
  green: '#22c55e'
};

const modeLabels = {
  ai: 'AI Mode',
  manual: 'Manual Mode',
  real: 'Real Mode'
};

const modeIcons = {
  ai: <FiZap className="w-6 h-6 text-green-500" />,
  manual: <FiSettings className="w-6 h-6 text-orange-500" />,
  real: <FiEye className="w-6 h-6 text-blue-500" />
};

const JunctionStatusPanel = ({ selectedJunction }) => {
  const { signalsVehicleData, cvData } = useSocket();
  
  // Simulate 4 signals per junction
  const [mode, setMode] = useState('ai');
  const [signals, setSignals] = useState([
    { id: 1, status: { red: true, yellow: false, green: false } },
    { id: 2, status: { red: false, yellow: true, green: false } },
    { id: 3, status: { red: false, yellow: false, green: true } },
    { id: 4, status: { red: true, yellow: false, green: false } }
  ]);

  // Get vehicle data for selected junction
  const getJunctionVehicleData = () => {
    if (!selectedJunction || !signalsVehicleData) return null;
    
    // Find matching signal data by ID or name
    const signalData = signalsVehicleData.signals_vehicle_data?.find(signal => 
      signal.signal_id === selectedJunction.id || 
      signal.signal_name === selectedJunction.name
    );
    
    if (signalData) {
      return {
        total: signalData.total_current || 0,
        density: signalData.traffic_density || 'unknown',
        hourly: signalData.total_hourly || 0,
        lanes: signalData.lanes || {}
      };
    }
    
    // Default data if no specific signal data found
    return {
      total: Math.floor(Math.random() * 30) + 10,
      density: 'medium',
      hourly: Math.floor(Math.random() * 400) + 200,
      lanes: {}
    };
  };

  const vehicleData = getJunctionVehicleData();

  // Get density color
  const getDensityColor = (density) => {
    switch (density) {
      case 'low': return 'text-green-600 bg-green-100';
      case 'medium': return 'text-yellow-600 bg-yellow-100';
      case 'high': return 'text-orange-600 bg-orange-100';
      case 'very_high': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  useEffect(() => {
    // Reset mode and signals when junction changes
    setMode('ai');
    setSignals([
      { id: 1, status: { red: true, yellow: false, green: false } },
      { id: 2, status: { red: false, yellow: true, green: false } },
      { id: 3, status: { red: false, yellow: false, green: true } },
      { id: 4, status: { red: true, yellow: false, green: false } }
    ]);
  }, [selectedJunction]);

  if (!selectedJunction) {
    return (
      <div className="bg-white rounded-xl shadow-lg p-6 w-full max-w-sm mx-auto flex flex-col justify-center items-center text-gray-500">
        <div className="mb-2">Select a junction on the map</div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl shadow-lg p-6 w-full max-w-sm mx-auto flex flex-col justify-center">
      <h3 className="text-lg font-semibold text-gray-800 mb-2">{selectedJunction.name}</h3>
      
      {/* Vehicle Count Section */}
      {vehicleData && (
        <div className="mb-4 p-3 bg-gray-50 rounded-lg">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center">
              <FiTruck className="w-5 h-5 text-blue-500 mr-2" />
              <span className="font-medium text-gray-700">Vehicle Count</span>
            </div>
            <span className={`px-2 py-1 rounded-full text-xs font-medium ${getDensityColor(vehicleData.density)}`}>
              {vehicleData.density.replace('_', ' ').toUpperCase()}
            </span>
          </div>
          <div className="grid grid-cols-2 gap-2 text-sm">
            <div className="text-center">
              <div className="text-2xl font-bold text-gray-900">{vehicleData.total}</div>
              <div className="text-gray-600">Current</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-gray-700">{vehicleData.hourly}</div>
              <div className="text-gray-600">Hourly Avg</div>
            </div>
          </div>
          {cvData && cvData.lane_counts && (
            <div className="mt-2 pt-2 border-t border-gray-200">
              <div className="text-xs text-green-600 font-medium mb-1">Live CV Detection:</div>
              <div className="flex justify-between text-xs">
                {Object.entries(cvData.lane_counts).map(([lane, count]) => (
                  <span key={lane} className="text-gray-600">
                    {lane.replace('_', ' ')}: {count}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
      
      <div className="mb-4">
        <div className="font-medium text-gray-700 mb-1">Signal Status:</div>
        <div className="grid grid-cols-2 gap-4">
          {signals.map((signal, idx) => (
            <div key={signal.id} className="border rounded-lg p-2 flex flex-col items-center">
              <span className="text-xs font-semibold text-gray-700 mb-1">Signal {signal.id}</span>
              <div className="flex space-x-2 items-center">
                <div className="flex flex-col items-center">
                  <span className="text-xs text-gray-600">Red</span>
                  <div style={{ background: signalColors.red }} className={`w-5 h-5 rounded-full border-2 ${signal.status.red ? 'border-red-500' : 'border-gray-300'} mb-1`} />
                </div>
                <div className="flex flex-col items-center">
                  <span className="text-xs text-gray-600">Yellow</span>
                  <div style={{ background: signalColors.yellow }} className={`w-5 h-5 rounded-full border-2 ${signal.status.yellow ? 'border-yellow-500' : 'border-gray-300'} mb-1`} />
                </div>
                <div className="flex flex-col items-center">
                  <span className="text-xs text-gray-600">Green</span>
                  <div style={{ background: signalColors.green }} className={`w-5 h-5 rounded-full border-2 ${signal.status.green ? 'border-green-500' : 'border-gray-300'} mb-1`} />
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
      <div className="mb-4">
        <div className="font-medium text-gray-700 mb-1">Mode:</div>
        <div className="flex space-x-2">
          {['ai', 'manual', 'real'].map(m => (
            <button
              key={m}
              onClick={() => setMode(m)}
              className={`flex flex-col items-center px-3 py-2 rounded-lg border ${mode === m ? 'bg-blue-100 border-blue-500' : 'bg-gray-50 border-gray-200'} transition-colors`}
            >
              {modeIcons[m]}
              <span className="text-xs mt-1 font-medium text-gray-700">{modeLabels[m]}</span>
            </button>
          ))}
        </div>
      </div>
      <div className="mb-2">
        <div className="font-medium text-gray-700 mb-1">Change Signal Status:</div>
        <div className="grid grid-cols-2 gap-2">
          {signals.map((signal, idx) => (
            <div key={signal.id} className="flex flex-col items-center">
              <span className="text-xs text-gray-600 mb-1">Signal {signal.id}</span>
              <div className="flex space-x-1">
                <button onClick={() => setSignals(signals.map((s, i) => i === idx ? { ...s, status: { red: true, yellow: false, green: false } } : s))} className="px-2 py-1 rounded bg-red-100 text-red-700 text-xs">Red</button>
                <button onClick={() => setSignals(signals.map((s, i) => i === idx ? { ...s, status: { red: false, yellow: true, green: false } } : s))} className="px-2 py-1 rounded bg-yellow-100 text-yellow-700 text-xs">Yellow</button>
                <button onClick={() => setSignals(signals.map((s, i) => i === idx ? { ...s, status: { red: false, yellow: false, green: true } } : s))} className="px-2 py-1 rounded bg-green-100 text-green-700 text-xs">Green</button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default JunctionStatusPanel;
