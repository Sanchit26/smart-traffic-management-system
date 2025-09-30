import React, { useState, useEffect } from 'react';
import io from 'socket.io-client';

const ManualSignalControl = () => {
  const [signalStates, setSignalStates] = useState({
    signal_1: { direction: 'North', state: 'red', timer: 0 },
    signal_2: { direction: 'East', state: 'red', timer: 0 },
    signal_3: { direction: 'South', state: 'red', timer: 0 },
    signal_4: { direction: 'West', state: 'red', timer: 0 }
  });
  
  const [manualMode, setManualMode] = useState(false);
  const [socket, setSocket] = useState(null);
  const [connectionStatus, setConnectionStatus] = useState('disconnected');
  const [simulationStatus, setSimulationStatus] = useState(null); // New state for simulation status

  useEffect(() => {
    // Initialize Socket.IO connection
    const newSocket = io('http://localhost:5050', {
      transports: ['polling']
    });

    newSocket.on('connect', () => {
      console.log('🎛️ Manual Control connected to backend');
      setConnectionStatus('connected');
    });

    newSocket.on('disconnect', () => {
      console.log('🎛️ Manual Control disconnected');
      setConnectionStatus('disconnected');
    });

    // Listen for signal state updates from simulation
    newSocket.on('signal_state_update', (data) => {
      console.log('📡 Received signal state update:', data);
      if (data.signals) {
        // Map simulation signal IDs (0,1,2,3) to our component format
        setSignalStates({
          signal_1: { direction: 'North', state: data.signals['0'] || 'red', timer: 0 },
          signal_2: { direction: 'East', state: data.signals['1'] || 'red', timer: 0 },
          signal_3: { direction: 'South', state: data.signals['2'] || 'red', timer: 0 },
          signal_4: { direction: 'West', state: data.signals['3'] || 'red', timer: 0 }
        });
      }
      if (typeof data.manual_mode === 'boolean') {
        setManualMode(data.manual_mode);
      }
    });

    // Listen for manual simulation status updates
    newSocket.on('manual_simulation_status', (data) => {
      console.log('🚀 Manual simulation status:', data);
      setSimulationStatus(data);
      
      // Clear status message after 5 seconds
      setTimeout(() => {
        setSimulationStatus(null);
      }, 5000);
    });

    setSocket(newSocket);

    // Cleanup on unmount
    return () => {
      newSocket.disconnect();
    };
  }, []);

  const changeSignalState = (signalId, newState) => {
    if (!socket || !manualMode) return;

    // Map component signal IDs to simulation IDs (signal_1 -> 0, signal_2 -> 1, etc.)
    const signalIdMap = {
      'signal_1': '0',  // North
      'signal_2': '1',  // East
      'signal_3': '2',  // South
      'signal_4': '3'   // West
    };

    const simulationSignalId = signalIdMap[signalId];
    if (!simulationSignalId) return;

    console.log(`🎛️ Changing signal ${signalId} (${simulationSignalId}) to ${newState}`);

    // Send manual signal change to backend
    socket.emit('manual_signal_change', {
      signal_id: simulationSignalId,
      new_state: newState,
      timestamp: Date.now()
    });

    // Update local state immediately for responsiveness
    setSignalStates(prev => ({
      ...prev,
      [signalId]: {
        ...prev[signalId],
        state: newState,
        timer: newState === 'green' ? 30 : newState === 'yellow' ? 5 : 60
      }
    }));

    console.log(`Manual signal change: ${signalId} -> ${newState}`);
  };

  const toggleManualMode = () => {
    const newMode = !manualMode;
    setManualMode(newMode);
    
    if (socket) {
      socket.emit('manual_mode_toggle', {
        manual_mode: newMode,
        timestamp: Date.now()
      });
    }

    console.log(`Manual mode: ${newMode ? 'ENABLED' : 'DISABLED'}`);
  };

  const getSignalColor = (state) => {
    switch (state) {
      case 'green': return 'bg-green-500 shadow-green-300';
      case 'yellow': return 'bg-yellow-500 shadow-yellow-300';
      case 'red': return 'bg-red-500 shadow-red-300';
      default: return 'bg-gray-400';
    }
  };

  const getSignalIcon = (state) => {
    switch (state) {
      case 'green': return '🟢';
      case 'yellow': return '🟡';
      case 'red': return '🔴';
      default: return '⚫';
    }
  };

  const resetAllSignals = () => {
    if (!socket || !manualMode) return;

    // Set all signals to red
    Object.keys(signalStates).forEach(signalId => {
      changeSignalState(signalId, 'red');
    });
  };

  const emergencyGreen = (signalId) => {
    if (!socket || !manualMode) return;

    // Set target signal to green, others to red
    Object.keys(signalStates).forEach(id => {
      changeSignalState(id, id === signalId ? 'green' : 'red');
    });
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold text-gray-800">
          🎛️ Manual Signal Control
        </h3>
        <div className="flex items-center space-x-2">
          <div className={`w-2 h-2 rounded-full ${
            connectionStatus === 'connected' ? 'bg-green-500' : 'bg-red-500'
          } animate-pulse`}></div>
          <span className={`text-sm font-medium ${
            connectionStatus === 'connected' ? 'text-green-600' : 'text-red-600'
          }`}>
            {connectionStatus}
          </span>
        </div>
      </div>

      {/* Manual Mode Toggle */}
      <div className="mb-6 p-4 bg-gray-50 rounded-lg">
        <div className="flex items-center justify-between">
          <div>
            <h4 className="font-medium text-gray-800">Manual Mode</h4>
            <p className="text-sm text-gray-600">
              {manualMode ? 'Override automatic signals' : 'Automatic signal control active'}
            </p>
          </div>
          <button
            onClick={toggleManualMode}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              manualMode 
                ? 'bg-orange-500 text-white hover:bg-orange-600' 
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            {manualMode ? 'MANUAL' : 'AUTO'}
          </button>
        </div>
      </div>

      {/* Simulation Status Message */}
      {simulationStatus && (
        <div className={`mb-4 p-3 rounded-lg ${
          simulationStatus.status === 'started' ? 'bg-green-100 text-green-800' :
          simulationStatus.status === 'error' ? 'bg-red-100 text-red-800' :
          'bg-blue-100 text-blue-800'
        }`}>
          <div className="flex items-center">
            <div className="text-sm font-medium">
              {simulationStatus.status === 'started' && '🚀 '}
              {simulationStatus.status === 'error' && '❌ '}
              {simulationStatus.status === 'already_running' && 'ℹ️ '}
              {simulationStatus.message}
            </div>
          </div>
        </div>
      )}

      {/* Quick Actions */}
      {manualMode && (
        <div className="mb-6 space-y-2">
          <button
            onClick={resetAllSignals}
            className="w-full px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors"
          >
            🛑 All Red (Emergency Stop)
          </button>
        </div>
      )}

      {/* Signal Controls */}
      <div className="space-y-4">
        {Object.entries(signalStates).map(([signalId, signal]) => (
          <div key={signalId} className="border rounded-lg p-4">
            {/* Signal Header */}
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center space-x-2">
                <span className="text-lg">{getSignalIcon(signal.state)}</span>
                <div>
                  <h4 className="font-medium text-gray-800">
                    Signal {signalId.split('_')[1]} - {signal.direction}
                  </h4>
                  <p className="text-sm text-gray-600">
                    Current: {signal.state.toUpperCase()} 
                    {signal.timer > 0 && ` (${signal.timer}s)`}
                  </p>
                </div>
              </div>
              {manualMode && (
                <button
                  onClick={() => emergencyGreen(signalId)}
                  className="px-3 py-1 bg-green-500 text-white text-xs rounded hover:bg-green-600 transition-colors"
                >
                  Emergency Green
                </button>
              )}
            </div>

            {/* Signal State Indicator */}
            <div className="flex items-center space-x-2 mb-3">
              <div className={`w-4 h-4 rounded-full ${getSignalColor(signal.state)} shadow-lg`}></div>
              <span className="text-sm font-medium text-gray-700">
                {signal.state.charAt(0).toUpperCase() + signal.state.slice(1)}
              </span>
            </div>

            {/* Manual Controls */}
            {manualMode && (
              <div className="grid grid-cols-3 gap-2">
                <button
                  onClick={() => changeSignalState(signalId, 'red')}
                  className={`px-3 py-2 rounded text-sm font-medium transition-colors ${
                    signal.state === 'red'
                      ? 'bg-red-500 text-white'
                      : 'bg-red-100 text-red-700 hover:bg-red-200'
                  }`}
                >
                  🔴 Red
                </button>
                <button
                  onClick={() => changeSignalState(signalId, 'yellow')}
                  className={`px-3 py-2 rounded text-sm font-medium transition-colors ${
                    signal.state === 'yellow'
                      ? 'bg-yellow-500 text-white'
                      : 'bg-yellow-100 text-yellow-700 hover:bg-yellow-200'
                  }`}
                >
                  🟡 Yellow
                </button>
                <button
                  onClick={() => changeSignalState(signalId, 'green')}
                  className={`px-3 py-2 rounded text-sm font-medium transition-colors ${
                    signal.state === 'green'
                      ? 'bg-green-500 text-white'
                      : 'bg-green-100 text-green-700 hover:bg-green-200'
                  }`}
                >
                  🟢 Green
                </button>
              </div>
            )}

            {/* Read-only mode indicator */}
            {!manualMode && (
              <div className="text-center py-2 bg-gray-100 rounded text-sm text-gray-600">
                Enable Manual Mode to Control
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Status Footer */}
      <div className="mt-6 pt-4 border-t text-xs text-gray-500">
        <div className="flex justify-between">
          <span>Mode: {manualMode ? 'Manual Control' : 'Automatic'}</span>
          <span>Connection: {connectionStatus}</span>
        </div>
        <div className="mt-1">
          Last Updated: {new Date().toLocaleTimeString()}
        </div>
      </div>
    </div>
  );
};

export default ManualSignalControl;