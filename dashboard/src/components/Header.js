import React from 'react';
import { motion } from 'framer-motion';
import { 
  FiMenu, 
  FiX, 
  FiMessageSquare, 
  FiTruck, 
  FiBarChart,
  FiWifi,
  FiWifiOff
} from 'react-icons/fi';
import { useSocket } from '../context/SocketContext';

const Header = ({ sidebarOpen, toggleSidebar, selectedPanel, setSelectedPanel }) => {
  const { connected } = useSocket();

  const panelButtons = [
    { id: 'chatbot', icon: FiMessageSquare, label: 'AI Assistant' },
    { id: 'emergency', icon: FiTruck, label: 'Emergency' },
    { id: 'analytics', icon: FiBarChart, label: 'Analytics' }
  ];

  return (
    <motion.header
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="fixed top-0 left-0 right-0 z-50 bg-white shadow-lg border-b border-gray-200"
    >
      <div className="flex items-center justify-between px-6 py-4">
        {/* Left Section */}
        <div className="flex items-center space-x-4">
          <button
            onClick={toggleSidebar}
            className="p-2 rounded-lg hover:bg-gray-100 transition-colors"
          >
            {sidebarOpen ? (
              <FiX className="w-6 h-6 text-gray-600" />
            ) : (
              <FiMenu className="w-6 h-6 text-gray-600" />
            )}
          </button>
          
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-blue-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-sm">🚦</span>
            </div>
            <div>
              <h1 className="text-xl font-bold text-gray-800">
                Smart Traffic Dashboard
              </h1>
              <p className="text-sm text-gray-500">Real-time Traffic Management System</p>
            </div>
          </div>
        </div>

        {/* Center Section - Panel Toggle Buttons */}
        <div className="flex items-center space-x-2">
          {panelButtons.map((panel) => {
            const Icon = panel.icon;
            const isActive = selectedPanel === panel.id;
            
            return (
              <motion.button
                key={panel.id}
                onClick={() => setSelectedPanel(panel.id)}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-all duration-200 ${
                  isActive
                    ? 'bg-blue-500 text-white shadow-md'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
              >
                <Icon className="w-4 h-4" />
                <span className="text-sm font-medium">{panel.label}</span>
              </motion.button>
            );
          })}
        </div>

        {/* Right Section */}
        <div className="flex items-center space-x-4">
          {/* Connection Status */}
          <div className="flex items-center space-x-2">
            {connected ? (
              <FiWifi className="w-5 h-5 text-green-500" />
            ) : (
              <FiWifiOff className="w-5 h-5 text-red-500" />
            )}
            <span className={`text-sm font-medium ${
              connected ? 'text-green-600' : 'text-red-600'
            }`}>
              {connected ? 'Connected' : 'Disconnected'}
            </span>
          </div>

          {/* Current Time */}
          <div className="text-sm text-gray-500">
            {new Date().toLocaleTimeString()}
          </div>
        </div>
      </div>
    </motion.header>
  );
};

export default Header;
