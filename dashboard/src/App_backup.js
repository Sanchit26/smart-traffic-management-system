import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import StatsCards from './components/StatsCards';
import TrafficMap from './components/TrafficMap';
import ChatbotFeed from './components/ChatbotFeed';
import AnalyticsPanel from './components/AnalyticsPanel';
import EmergencyTracking from './components/EmergencyTracking';
import Header from './components/Header';
import { SocketProvider } from './context/SocketContext';
import './index.css';
import JunctionStatusPanel from './components/JunctionStatusPanel';
import Login from './components/Auth/Login';
import IndianVehicleDisplay from './components/IndianVehicleDisplay';
import ManualSignalControl from './components/ManualSignalControl';

// DashboardApp: the main dashboard UI, shown after login
function DashboardApp({ onLogout }) {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [selectedPanel, setSelectedPanel] = useState('automation');
  const [selectedJunction, setSelectedJunction] = useState(null);

  const toggleSidebar = () => {
    setSidebarOpen(!sidebarOpen);
  };

  return (
    <SocketProvider>
      <div className="min-h-screen bg-gray-50 flex flex-col">
        <ToastContainer
          position="top-right"
          autoClose={3000}
          hideProgressBar={false}
          newestOnTop
          closeOnClick
          rtl={false}
          pauseOnFocusLoss
          draggable
          pauseOnHover
          theme="light"
        />
        {/* Header */}
        <Header 
          sidebarOpen={sidebarOpen}
          toggleSidebar={toggleSidebar}
          selectedPanel={selectedPanel}
          setSelectedPanel={setSelectedPanel}
        />

        {/* Main Content Layout */}
        <div className="flex flex-1 pt-16">
          {/* Sidebar Navigation */}
          <div className={`transition-all duration-300 bg-white border-r border-gray-200 ${sidebarOpen ? 'w-64' : 'w-20'} flex flex-col`}>
            <nav className="flex-1 p-4 space-y-2">
              <button className={`w-full text-left px-4 py-2 rounded-lg font-medium ${selectedPanel === 'automation' ? 'bg-blue-100 text-blue-700' : 'text-gray-700 hover:bg-gray-100'}`} onClick={() => setSelectedPanel('automation')}>Automation</button>
              <button className={`w-full text-left px-4 py-2 rounded-lg font-medium ${selectedPanel === 'analytics' ? 'bg-blue-100 text-blue-700' : 'text-gray-700 hover:bg-gray-100'}`} onClick={() => setSelectedPanel('analytics')}>Analytics</button>
              <button className={`w-full text-left px-4 py-2 rounded-lg font-medium ${selectedPanel === 'chatbot' ? 'bg-blue-100 text-blue-700' : 'text-gray-700 hover:bg-gray-100'}`} onClick={() => setSelectedPanel('chatbot')}>AI Assistant</button>
              <button className={`w-full text-left px-4 py-2 rounded-lg font-medium ${selectedPanel === 'emergency' ? 'bg-blue-100 text-blue-700' : 'text-gray-700 hover:bg-gray-100'}`} onClick={() => setSelectedPanel('emergency')}>Emergency</button>
              <button className={`w-full text-left px-4 py-2 rounded-lg font-medium ${selectedPanel === 'manual' ? 'bg-blue-100 text-blue-700' : 'text-gray-700 hover:bg-gray-100'}`} onClick={() => setSelectedPanel('manual')}>Manual Control</button>
            </nav>
          </div>

          {/* Main Dashboard Area */}
          <div className="flex-1 flex flex-col p-6">
            {/* Map and Mode Toggle Row */}
            <div className="flex flex-row gap-6 mb-6">
              {/* Map */}
              <div className="flex-1 bg-white rounded-xl shadow-lg overflow-hidden" style={{ minHeight: '600px', height: '600px' }}>
                <TrafficMap selectedJunction={selectedJunction} setSelectedJunction={setSelectedJunction} />
              </div>
              {/* Junction Status Panel */}
              <div className="w-80 space-y-4">
                <JunctionStatusPanel selectedJunction={selectedJunction} />
              </div>
            </div>
            
            {/* Indian Traffic Detection Container - Main Center Area */}
            <div className="mb-6">
              <IndianVehicleDisplay />
            </div>
            
            {/* Stats Cards below */}
            <div className="mb-6">
              <StatsCards />
            </div>
            {/* Analytics Panel (only on Analytics page) */}
            {selectedPanel === 'analytics' && (
              <div className="mt-6">
                <AnalyticsPanel />
              </div>
            )}
            {/* Chatbot and Emergency Panels */}
            {selectedPanel === 'chatbot' && (
              <div className="mt-6">
                <ChatbotFeed />
              </div>
            )}
            {selectedPanel === 'emergency' && (
              <div className="mt-6">
                <EmergencyTracking />
              </div>
            )}
            {/* Manual Control Panel */}
            {selectedPanel === 'manual' && (
              <div className="mt-6">
                <ManualSignalControl />
              </div>
            )}
          </div>
        </div>
      </div>
    </SocketProvider>
  );
}

// App: handles routing and authentication state
function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  const handleLogin = () => setIsAuthenticated(true);
  const handleLogout = () => setIsAuthenticated(false);

  return (
    <Router>
      <Routes>
        <Route
          path="/"
          element={
            isAuthenticated ? (
              <Navigate to="/dashboard" replace />
            ) : (
              <Login onLogin={handleLogin} />
            )
          }
        />
        <Route
          path="/dashboard"
          element={
            isAuthenticated ? (
              <DashboardApp onLogout={handleLogout} />
            ) : (
              <Navigate to="/" replace />
            )
          }
        />
      </Routes>
    </Router>
  );
}

export default App;
