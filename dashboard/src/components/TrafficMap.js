import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import L from 'leaflet';
import { 
  FiWind, 
  FiTruck, 
  FiClock
} from 'react-icons/fi';
import { useSocket } from '../context/SocketContext';
import axios from 'axios';

// Fix for default markers in react-leaflet
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

// Custom camera icon for traffic signals
const createCameraIcon = (color = 'blue', isCCTV = false) => {
  if (isCCTV) {
    return L.divIcon({
      className: 'custom-cctv-marker animated-cctv',
      html: `
        <div class="cctv-outer w-12 h-12 rounded-full border-2 border-white shadow-lg flex items-center justify-center group" style="background-color: ${color}; transition: transform 0.3s;">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" class="w-10 h-10 realistic-cctv">
            <rect x="10" y="24" width="44" height="12" rx="6" fill="#222" stroke="#fff" stroke-width="2"/>
            <rect x="24" y="36" width="16" height="8" rx="4" fill="#888" stroke="#fff" stroke-width="2"/>
            <circle cx="32" cy="30" r="4" fill="#0ff" stroke="#fff" stroke-width="1"/>
            <rect x="28" y="44" width="8" height="6" rx="2" fill="#222" stroke="#fff" stroke-width="1"/>
          </svg>
          <style>
            .custom-cctv-marker .cctv-outer:hover {
              transform: scale(1.15) rotate(-10deg);
              box-shadow: 0 0 16px 2px #0ff;
            }
            .custom-cctv-marker .realistic-cctv {
              transition: filter 0.3s;
            }
            .custom-cctv-marker .cctv-outer:hover .realistic-cctv {
              filter: drop-shadow(0 0 6px #0ff);
            }
          </style>
        </div>
      `,
      iconSize: [48, 48],
      iconAnchor: [24, 24],
      popupAnchor: [0, -24]
    });
  }
// Add animated effect for CCTV marker
if (typeof window !== 'undefined') {
  const style = document.createElement('style');
  style.innerHTML = `
    .animated-cctv .cctv-outer:hover {
      transform: scale(1.15) rotate(-10deg);
      box-shadow: 0 0 16px 2px #0ff;
    }
    .animated-cctv .realistic-cctv {
      transition: filter 0.3s;
    }
    .animated-cctv .cctv-outer:hover .realistic-cctv {
      filter: drop-shadow(0 0 6px #0ff);
    }
  `;
  document.head.appendChild(style);
}
  // Default camera icon
  return L.divIcon({
    className: 'custom-camera-marker',
    html: `
      <div class="w-8 h-8 rounded-full border-2 border-white shadow-lg flex items-center justify-center" style="background-color: ${color};">
        <svg class="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M4 3a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V5a2 2 0 00-2-2H4zm12 12H4l4-8 3 6 2-4 3 6z" clip-rule="evenodd"></path>
        </svg>
      </div>
    `,
    iconSize: [32, 32],
    iconAnchor: [16, 16],
    popupAnchor: [0, -16]
  });
};

// Custom emergency vehicle icon
const createEmergencyIcon = (type) => {
  const colors = {
    ambulance: '#ef4444',
    fire_truck: '#dc2626',
    police: '#3b82f6'
  };
  
  return L.divIcon({
    className: 'custom-emergency-marker',
    html: `
      <div class="w-6 h-6 rounded-full border-2 border-white shadow-lg flex items-center justify-center animate-pulse" style="background-color: ${colors[type] || '#6b7280'};">
        <span class="text-white text-xs font-bold">${type === 'ambulance' ? 'A' : type === 'fire_truck' ? 'F' : 'P'}</span>
      </div>
    `,
    iconSize: [24, 24],
    iconAnchor: [12, 12]
  });
};

// Camera locations defined outside component to avoid dependency issues
const narsingiCamera = {
  id: 'narsingi-1',
  name: 'Narsingi Junction',
  lat: 17.385546,
  lng: 78.354630,
  type: 'simulation',
  co2_level: 0,
  vehicles_detected: 0,
  queue_length: 0
};

const secondCamera = {
  id: 'cctv-2',
  name: 'Main Road Junction',
  lat: 17.385000,
  lng: 78.355000,
  type: 'cctv',
  co2_level: 95,
  vehicles_detected: 45,
  queue_length: 8
};

const thirdCamera = {
  id: 'cctv-3',
  name: 'Metro Station Junction',
  lat: 17.384000,
  lng: 78.356000,
  type: 'cctv',
  co2_level: 110,
  vehicles_detected: 60,
  queue_length: 12
};

const TrafficMap = ({ selectedJunction, setSelectedJunction }) => {
  const { signals, cvData } = useSocket();
  const [selectedSignal, setSelectedSignal] = useState(null);
  const [showCCTV, setShowCCTV] = useState(false);
  const [showSimulation, setShowSimulation] = useState(false);
  const [simulationStatus, setSimulationStatus] = useState(null); // 'loading' | 'success' | 'error' | null
  const [showOptionsModal, setShowOptionsModal] = useState(false);
  // eslint-disable-next-line no-unused-vars
  const [dataSource, setDataSource] = useState('auto'); // 'cv', 'simulation', 'auto'

  // Effect: When selectedJunction changes, select the signal and show simulation
  useEffect(() => {
    if (selectedJunction) {
      // Find the camera object for the selected junction
      let signal = null;
      if (selectedJunction.id === 'narsingi-1') signal = narsingiCamera;
      else if (selectedJunction.id === 'cctv-2') signal = secondCamera;
      else if (selectedJunction.id === 'cctv-3') signal = thirdCamera;
      if (signal) {
        setSelectedSignal(signal);
        setShowSimulation(false); // Only show pop-up, not simulation container
      }
    }
  }, [selectedJunction]);
  
  const getCO2Color = (level) => {
    if (level < 90) return '#22c55e'; // green
    if (level < 110) return '#f59e0b'; // yellow
    return '#ef4444'; // red
  };

  const handleSignalClick = (signal) => {
    setSelectedSignal(signal);
    setShowSimulation(false);
    setShowCCTV(false);
    setShowOptionsModal(true);
  };

  const handleCCTVOption = () => {
    setShowOptionsModal(false);
    setShowCCTV(true);
    // Set data source to CV for this session
    setDataSource('cv');
  };

  const handleSimulationOption = async () => {
    setShowOptionsModal(false);
    setSimulationStatus('loading');
    
    try {
      const resp = await axios.post('http://localhost:5050/api/start-simulation');
      if (resp.data && resp.data.status === 'success') {
        setSimulationStatus('success');
        // Set data source to simulation for this session
        setDataSource('simulation');
      } else {
        setSimulationStatus('error');
      }
    } catch (e) {
      setSimulationStatus('error');
    }
    setShowSimulation(true);
  };

  return (
    <div className="h-full flex flex-col">
      {/* Overlay for closing simulation */}
      {showSimulation && (
        <div
          className="fixed inset-0 z-40 bg-black bg-opacity-10 cursor-pointer"
          onClick={() => {
            setShowSimulation(false);
            setSelectedSignal(null);
            setSimulationStatus(null);
          }}
        />
      )}
      {/* Header */}
      <div className="p-6 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-semibold text-gray-800">Traffic Map</h2>
            <p className="text-sm text-gray-600">Real-time traffic signal monitoring</p>
          </div>
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 rounded-full bg-green-500"></div>
              <span className="text-sm text-gray-600">Good Air Quality</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 rounded-full bg-yellow-500"></div>
              <span className="text-sm text-gray-600">Moderate</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 rounded-full bg-red-500"></div>
              <span className="text-sm text-gray-600">High Pollution</span>
            </div>
          </div>
        </div>
      </div>

      {/* Map Container */}
      <div className="flex-1 relative">
        <MapContainer
          center={showSimulation || true ? [narsingiCamera.lat, narsingiCamera.lng] : [17.385044, 78.486671]}
          zoom={showSimulation || true ? 16 : 13}
          style={{ height: '100%', width: '100%' }}
          className="z-0"
        >
        {/* Third CCTV Camera Marker */}
            <Marker
              key={thirdCamera.id}
              position={[thirdCamera.lat, thirdCamera.lng]}
              icon={createCameraIcon('blue', true)}
              eventHandlers={{
                click: () => setSelectedJunction(thirdCamera)
              }}
            >
              <Popup>
                <div className="relative p-4 w-80 min-w-[320px]">
                  <button
                    onClick={() => setSelectedJunction(null)}
                    className="absolute top-2 right-2 text-gray-400 hover:text-red-600 bg-gray-100 rounded-full p-1 z-10"
                    title="Cancel"
                  >
                    <span className="sr-only">Cancel</span>
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" /></svg>
                  </button>
                  <h3 className="font-semibold text-gray-800 text-lg">{thirdCamera.name}</h3>
                  <div className="mt-2 space-y-2 text-base">
                    <div className="flex items-center space-x-2">
                      <span role="img" aria-label="camera">📷</span>
                      <span>Camera Simulation</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <span>CO₂: {thirdCamera.co2_level} ppm</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <span>Vehicles: {thirdCamera.vehicles_detected}</span>
                    </div>
                  </div>
                  <div className="flex gap-2 mt-4">
                    <button
                      onClick={() => handleSignalClick(thirdCamera)}
                      className="w-1/2 bg-blue-500 text-white px-3 py-2 rounded text-sm hover:bg-blue-600 transition-colors"
                    >
                      Open SUMO Simulation
                    </button>
                    <button
                      onClick={() => { setSelectedSignal(thirdCamera); setShowCCTV(true); setShowSimulation(false); }}
                      className="w-1/2 bg-green-500 text-white px-3 py-2 rounded text-sm hover:bg-green-600 transition-colors"
                    >
                      CCTV
                    </button>
                  </div>
                </div>
              </Popup>
            </Marker>
          <TileLayer
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          />
          
          {/* Narsingi Camera Marker */}
          <Marker
            key={narsingiCamera.id}
            position={[narsingiCamera.lat, narsingiCamera.lng]}
            icon={createCameraIcon('blue', true)}
            eventHandlers={{
              click: () => setSelectedJunction(narsingiCamera)
            }}
          >
            <Popup>
              <div className="p-4 w-80 min-w-[320px]">
                <h3 className="font-semibold text-gray-800 text-lg">{narsingiCamera.name}</h3>
                <div className="mt-2 space-y-2 text-base">
                  <div className="flex items-center space-x-2">
                    <span role="img" aria-label="camera">📷</span>
                    <span>Camera Simulation</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span>CO₂: {narsingiCamera.co2_level} ppm</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span>Vehicles: {narsingiCamera.vehicles_detected}</span>
                  </div>
                </div>
                <div className="flex gap-2 mt-4">
                  <button
                    onClick={() => handleSignalClick(narsingiCamera)}
                    className="w-1/2 bg-blue-500 text-white px-3 py-2 rounded text-sm hover:bg-blue-600 transition-colors"
                  >
                    Open SUMO Simulation
                  </button>
                  <button
                    onClick={() => { setSelectedSignal(narsingiCamera); setShowCCTV(true); setShowSimulation(false); }}
                    className="w-1/2 bg-green-500 text-white px-3 py-2 rounded text-sm hover:bg-green-600 transition-colors"
                  >
                    CCTV
                  </button>
                </div>
              </div>
            </Popup>
          </Marker>

          {/* Second CCTV Camera Marker */}
          <Marker
            key={secondCamera.id}
            position={[secondCamera.lat, secondCamera.lng]}
            icon={createCameraIcon('blue', true)}
            eventHandlers={{
              click: () => setSelectedJunction(secondCamera)
            }}
          >
            <Popup>
              <div className="p-4 w-80 min-w-[320px]">
                <h3 className="font-semibold text-gray-800 text-lg">{secondCamera.name}</h3>
                <div className="mt-2 space-y-2 text-base">
                  <div className="flex items-center space-x-2">
                    <span role="img" aria-label="camera">📷</span>
                    <span>Camera Simulation</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span>CO₂: {secondCamera.co2_level} ppm</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span>Vehicles: {secondCamera.vehicles_detected}</span>
                  </div>
                </div>
                <div className="flex gap-2 mt-4">
                  <button
                    onClick={() => handleSignalClick(secondCamera)}
                    className="w-1/2 bg-blue-500 text-white px-3 py-2 rounded text-sm hover:bg-blue-600 transition-colors"
                  >
                    Open SUMO Simulation
                  </button>
                  <button
                    onClick={() => { setSelectedSignal(secondCamera); setShowCCTV(true); setShowSimulation(false); }}
                    className="w-1/2 bg-green-500 text-white px-3 py-2 rounded text-sm hover:bg-green-600 transition-colors"
                  >
                    CCTV
                  </button>
                </div>
              </div>
            </Popup>
          </Marker>

          {/* Traffic Signal Markers */}
          {signals && signals.length > 0 && signals.map((signal) => (
            <Marker
              key={signal.id}
              position={[signal.lat, signal.lng]}
              icon={createCameraIcon(getCO2Color(signal.co2_level))}
              eventHandlers={{
                click: () => handleSignalClick(signal)
              }}
            >
              <Popup>
                <div className="p-2">
                  <h3 className="font-semibold text-gray-800">{signal.name}</h3>
                  <div className="mt-2 space-y-1 text-sm">
                    <div className="flex items-center space-x-2">
                      <FiTruck className="w-4 h-4 text-blue-500" />
                      <span>{signal.vehicles_detected} vehicles</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <FiWind className="w-4 h-4 text-green-500" />
                      <span>CO₂: {signal.co2_level} ppm</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <FiClock className="w-4 h-4 text-orange-500" />
                      <span>Queue: {signal.queue_length} vehicles</span>
                    </div>
                  </div>
                  <button
                    onClick={() => handleSignalClick(signal)}
                    className="mt-2 w-full bg-blue-500 text-white px-3 py-1 rounded text-sm hover:bg-blue-600 transition-colors"
                  >
                    View Camera Feed
                  </button>
                </div>
              </Popup>
            </Marker>
          ))}

          {/* Emergency Vehicle Markers - using signals data or empty array */}
          {signals && signals.emergency_vehicles && signals.emergency_vehicles.length > 0 && signals.emergency_vehicles.map((vehicle) => (
            <Marker
              key={vehicle.id}
              position={[vehicle.lat, vehicle.lng]}
              icon={createEmergencyIcon(vehicle.type)}
            >
              <Popup>
                <div className="p-2">
                  <h3 className="font-semibold text-gray-800">
                    {vehicle.type === 'ambulance' ? '🚑 Ambulance' : 
                     vehicle.type === 'fire_truck' ? '🚒 Fire Truck' : '🚔 Police'}
                  </h3>
                  <div className="mt-2 space-y-1 text-sm">
                    <div>ID: {vehicle.id}</div>
                    <div>Status: {vehicle.status}</div>
                    <div>Destination: {vehicle.destination}</div>
                    <div>ETA: {vehicle.eta}</div>
                  </div>
                </div>
              </Popup>
            </Marker>
          ))}
        </MapContainer>

        {/* Options Modal */}
        {showOptionsModal && selectedSignal && (
          <div className="absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-xl shadow-2xl p-8 max-w-md w-full mx-4">
              <h3 className="text-xl font-bold text-gray-800 mb-6 text-center">
                Select View Option for {selectedSignal.name}
              </h3>
              <div className="space-y-4">
                <button
                  onClick={handleCCTVOption}
                  className="w-full bg-blue-500 hover:bg-blue-600 text-white px-6 py-3 rounded-lg transition-colors flex items-center justify-center space-x-2"
                >
                  <FiWind className="w-5 h-5" />
                  <span>Open CCTV Feed (AI Analysis)</span>
                </button>
                <button
                  onClick={handleSimulationOption}
                  className="w-full bg-green-500 hover:bg-green-600 text-white px-6 py-3 rounded-lg transition-colors flex items-center justify-center space-x-2"
                >
                  <FiTruck className="w-5 h-5" />
                  <span>Traffic Simulation</span>
                </button>
                <button
                  onClick={() => setShowOptionsModal(false)}
                  className="w-full bg-gray-300 hover:bg-gray-400 text-gray-700 px-6 py-3 rounded-lg transition-colors"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Camera Feed or Simulation Modal */}
        {showSimulation && selectedSignal && (
          <div className="absolute top-8 right-8 bg-white rounded-xl shadow-2xl border border-gray-200 p-8 w-3/4 max-w-5xl z-50">
            <button
              onClick={() => {
                setShowSimulation(false);
              }}
              className="absolute top-4 right-4 text-gray-500 hover:text-red-600 bg-gray-100 rounded-full p-2 z-10"
              title="Cancel"
            >
              <span className="sr-only">Cancel</span>
              <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" /></svg>
            </button>
            <div className="flex items-center justify-between mb-6">
              <h3 className="font-bold text-2xl text-gray-800">SUMO Traffic Simulation</h3>
            </div>
            <div className="bg-gray-900 rounded-xl aspect-video flex items-center justify-center mb-6">
              <div className="text-white text-center">
                <div className="text-2xl mb-2">SUMO Simulation</div>
                <p className="text-lg text-gray-400">{selectedSignal.name} Traffic Simulation</p>
              </div>
            </div>
          </div>
        )}
        {showCCTV && selectedSignal && (
          <div className="absolute top-8 right-8 bg-white rounded-xl shadow-2xl border border-gray-200 p-8 w-3/4 max-w-5xl z-50">
            <button
              onClick={() => {
                setShowCCTV(false);
              }}
              className="absolute top-4 right-4 text-gray-500 hover:text-red-600 bg-gray-100 rounded-full p-2 z-10"
              title="Cancel"
            >
              <span className="sr-only">Cancel</span>
              <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" /></svg>
            </button>
            <div className="flex items-center justify-between mb-6">
              <h3 className="font-bold text-2xl text-gray-800">AI-Powered CCTV Feed</h3>
              <div className="text-sm text-gray-600">
                {cvData && cvData.lane_counts && (
                  <span>Vehicles: {Object.values(cvData.lane_counts).reduce((a, b) => a + b, 0)}</span>
                )}
              </div>
            </div>
            <div className="bg-gray-900 rounded-xl aspect-video flex items-center justify-center mb-6 overflow-hidden">
              <img
                src="http://localhost:5050/api/cv-stream"
                alt="AI-processed CCTV feed"
                className="w-full h-full object-cover"
                style={{ maxWidth: '100%', maxHeight: '100%' }}
              />
            </div>
            {cvData && cvData.lane_counts && (
              <div className="bg-gray-50 rounded-lg p-4">
                <h4 className="font-semibold text-gray-800 mb-2">Lane Analysis</h4>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  {Object.entries(cvData.lane_counts).map(([lane, count]) => (
                    <div key={lane} className="text-center">
                      <div className="text-lg font-bold text-blue-600">{count}</div>
                      <div className="text-sm text-gray-600">{lane.replace('_', ' ')}</div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Simulation Panel Feedback */}
      {showSimulation && simulationStatus === 'loading' && (
        <div className="fixed top-20 right-10 bg-blue-100 text-blue-800 px-4 py-2 rounded shadow z-50">Launching simulation...</div>
      )}
      {showSimulation && simulationStatus === 'success' && (
        <div className="fixed top-20 right-10 bg-green-100 text-green-800 px-4 py-2 rounded shadow z-50">Simulation started!</div>
      )}
      {showSimulation && simulationStatus === 'error' && (
        <div className="fixed top-20 right-10 bg-red-100 text-red-800 px-4 py-2 rounded shadow z-50">Failed to start simulation.</div>
      )}
    </div>
  );
};

export default TrafficMap;
