import React, { createContext, useContext, useEffect, useState } from 'react';
import { io } from 'socket.io-client';

const SocketContext = createContext();

export const useSocket = () => {
  const context = useContext(SocketContext);
  if (!context) {
    throw new Error('useSocket must be used within a SocketProvider');
  }
  return context;
};

export const SocketProvider = ({ children }) => {
  const [socket, setSocket] = useState(null);
  const [connected, setConnected] = useState(false);
  const [stats, setStats] = useState({
    vehicles_detected: 0,
    co2_saved: 0,
    avg_wait_time: 0,
    mode: 'automation'
  });
  const [signals, setSignals] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [emergencyVehicles, setEmergencyVehicles] = useState([]);
  const [cvData, setCvData] = useState(null);
  const [signalsVehicleData, setSignalsVehicleData] = useState(null);

  // Fetch signals vehicle data
  const fetchSignalsVehicleData = async () => {
    try {
      const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:5050';
      const response = await fetch(`${apiUrl}/api/signals-vehicle-data`);
      if (response.ok) {
        const data = await response.json();
        setSignalsVehicleData(data);
        // Update stats with total vehicles from signals data
        if (data.system_totals) {
          setStats(prev => ({
            ...prev,
            vehicles_detected: data.system_totals.total_vehicles_detected || prev.vehicles_detected
          }));
        }
      }
    } catch (error) {
      console.error('Error fetching signals vehicle data:', error);
    }
  };

  useEffect(() => {
    const socketUrl = process.env.REACT_APP_SOCKET_URL || 'http://localhost:5050';
    const newSocket = io(socketUrl, {
      transports: ['websocket'],
      autoConnect: true,
      reconnection: true,
      reconnectionDelay: 1000,
      reconnectionAttempts: 5
    });

    newSocket.on('connect', () => {
      console.log('Connected to server');
      setConnected(true);
      newSocket.emit('subscribe_to_updates');
    });

    newSocket.on('disconnect', () => {
      console.log('Disconnected from server');
      setConnected(false);
    });

    newSocket.on('connect_error', (error) => {
      console.error('Connection error:', error);
      setConnected(false);
    });

    newSocket.on('reconnect', () => {
      console.log('Reconnected to server');
      setConnected(true);
      newSocket.emit('subscribe_to_updates');
    });

    newSocket.on('stats_update', (data) => {
      // Use real vehicle detection data from backend
      setStats(prev => ({
        ...prev,
        vehicles_detected: data.vehicles_detected || 0,
        co2_saved: data.co2_saved || 0,
        avg_wait_time: data.avg_wait_time || 0,
        mode: data.mode || prev.mode
      }));
    });

    newSocket.on('signals_update', (data) => {
      setSignals(data.signals);
      if (data.emergency_vehicles) {
        setEmergencyVehicles(data.emergency_vehicles);
      }
    });

    newSocket.on('new_alert', (alert) => {
      setAlerts(prev => [alert, ...prev.slice(0, 19)]);
    });

    newSocket.on('mode_changed', (data) => {
      setStats(prev => ({ ...prev, mode: data.mode }));
    });

    newSocket.on('cv_frame_update', (data) => {
      setCvData(data);
      // Also refresh signals vehicle data when CV updates
      fetchSignalsVehicleData();
    });

    // Handle emergency alerts from simulation
    newSocket.on('emergency_alert', (alert) => {
      console.log('Emergency alert received:', alert);
      setAlerts(prev => [alert, ...prev.slice(0, 19)]);
      
      // Show browser notification if supported
      if ('Notification' in window && Notification.permission === 'granted') {
        new Notification('Emergency Alert', {
          body: alert.message,
          icon: '/logo192.png'
        });
      }
    });

    newSocket.on('emergency_cleared', (data) => {
      console.log('Emergency cleared:', data);
    });

    setSocket(newSocket);

    // Initial fetch of signals vehicle data
    fetchSignalsVehicleData();
    
    // Set up interval to periodically fetch signals data
    const signalsDataInterval = setInterval(fetchSignalsVehicleData, 5000);

    return () => {
      clearInterval(signalsDataInterval);
      newSocket.close();
    };
  }, []);

  const value = {
    socket,
    connected,
    stats,
    signals,
    alerts,
    emergencyVehicles,
    cvData,
    signalsVehicleData,
    setStats,
    setSignals,
    setAlerts,
    setEmergencyVehicles,
    setCvData,
    setSignalsVehicleData,
    fetchSignalsVehicleData
  };

  return (
    <SocketContext.Provider value={value}>
      {children}
    </SocketContext.Provider>
  );
};
