import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { FiZap, FiSettings, FiShield } from 'react-icons/fi';
import { useSocket } from '../context/SocketContext';
import axios from 'axios';
import { toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

const ModeToggle = ({ selectedJunction, setSelectedJunction }) => {
  // List of junctions
  const junctions = [
    { id: 'narsingi-1', name: 'Narsingi Junction' },
    { id: 'cctv-2', name: 'Mehdipatnam Junction' },
    { id: 'cctv-3', name: 'Moosarambagh Junction' }
  ];
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  // selectedJunction and setSelectedJunction now come from props

  // Filtered junctions for search
  const filteredJunctions = junctions.filter(j =>
    j.name.toLowerCase().includes(searchTerm.toLowerCase())
  );
  const { stats } = useSocket();

  const [isLoading, setIsLoading] = useState(false);

  const toggleMode = async () => {
    setIsLoading(true);
    try {
      const newMode = stats.mode === 'automation' ? 'manual' : 'automation';
      const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:5050';
      await axios.post(`${apiUrl}/api/mode`, { mode: newMode });
      toast.success(`Switched to ${newMode} mode`);
    } catch (err) {
      toast.error('Failed to toggle mode');
    }
    setIsLoading(false);
  } // <-- removed stray bracket

  // Handle junction selection
  const handleJunctionSelect = (junction) => {
  setSelectedJunction(junction);
  setDropdownOpen(false);
  toast.info(`Opening simulation for ${junction.name}`);
  } // <-- removed extra bracket

  const isAutomation = stats.mode === 'automation';

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.5 }}
      className="bg-white rounded-xl shadow-lg p-6 w-full max-w-sm mx-auto flex flex-col justify-center"
    >
      <div className="flex flex-col w-full">
        <div className="flex items-center justify-between w-full">
          <div className="flex items-center space-x-2">
            <div className={`p-3 rounded-lg ${isAutomation ? 'bg-green-50' : 'bg-orange-50'}`}>
              {isAutomation ? (
                <FiZap className="w-6 h-6 text-green-500" />
              ) : (
                <FiSettings className="w-6 h-6 text-orange-500" />
              )}
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-800">
                Traffic Control Mode
              </h3>
              <p className="text-sm text-gray-600">
                {isAutomation 
                  ? 'AI is currently managing traffic signals automatically'
                  : 'Manual control is active - human operators have override control'
                }
              </p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <div className={`w-3 h-3 rounded-full ${
              isAutomation ? 'bg-green-500' : 'bg-orange-500'
            } ${isAutomation ? 'glow-green' : 'glow-orange'}`} />
            <span className={`text-sm font-medium ${
              isAutomation ? 'text-green-600' : 'text-orange-600'
            }`}>
              {isAutomation ? 'AUTOMATION' : 'MANUAL'}
            </span>
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={toggleMode}
              disabled={isLoading}
              className={`relative inline-flex h-6 w-9 items-center rounded-full transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 ${
                isAutomation ? 'bg-green-500' : 'bg-orange-500'
              } ${isLoading ? 'opacity-50 cursor-not-allowed' : ''}`}
            >
              <motion.span
                animate={{
                  x: isAutomation ? 15 : 2,
                }}
                transition={{
                  type: "spring",
                  stiffness: 500,
                  damping: 30
                }}
                className={`inline-block h-4 w-4 transform rounded-full bg-white shadow-lg ${
                  isLoading ? 'animate-pulse' : ''
                }`}
              >
                {isLoading && (
                  <div className="absolute inset-0 flex items-center justify-center">
                    <div className="w-2.5 h-2.5 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
                  </div>
                )}
              </motion.span>
            </motion.button>
            {/* Dropdown for junction selection */}
            {dropdownOpen && (
              <div className="absolute z-50 mt-12 right-0 w-64 bg-white border border-gray-200 rounded-lg shadow-lg p-4">
                <input
                  type="text"
                  placeholder="Search junction..."
                  value={searchTerm}
                  onChange={e => setSearchTerm(e.target.value)}
                  className="w-full mb-2 px-3 py-2 border rounded focus:outline-none focus:ring"
                />
                <div className="max-h-48 overflow-y-auto">
                  {filteredJunctions.length === 0 ? (
                    <div className="text-gray-500 text-sm">No junctions found.</div>
                  ) : (
                    filteredJunctions.map(junction => (
                      <button
                        key={junction.id}
                        onClick={() => handleJunctionSelect(junction)}
                        className="w-full text-left px-3 py-2 rounded hover:bg-blue-100"
                      >
                        {junction.name}
                      </button>
                    ))
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Mode Description */}
      <div className="mt-4 p-4 bg-gray-50 rounded-lg">
        <div className="flex items-start space-x-3">
          <FiShield className="w-5 h-5 text-blue-500 mt-0.5" />
          <div>
            <h4 className="font-medium text-gray-800">
              {isAutomation ? 'Automation Mode Active' : 'Manual Mode Active'}
            </h4>
            <p className="text-sm text-gray-600 mt-1">
              {isAutomation 
                ? 'AI algorithms are continuously analyzing traffic patterns and optimizing signal timing to reduce congestion and emissions. Emergency vehicles are automatically prioritized.'
                : 'Traffic signals are under manual control. Operators can override AI decisions and manually adjust timing based on real-time conditions and emergency situations.'
              }
            </p>
          </div>
        </div>
      </div>

      {/* Performance Metrics */}
      <div className="mt-4 grid grid-cols-2 gap-4">
        <div className="text-center p-3 bg-gray-50 rounded-lg">
          <div className="text-lg font-semibold text-gray-800">
            {isAutomation ? '98.5%' : '94.2%'}
          </div>
          <div className="text-xs text-gray-600">Efficiency</div>
        </div>
        <div className="text-center p-3 bg-gray-50 rounded-lg">
          <div className="text-lg font-semibold text-gray-800">
            {isAutomation ? '12%' : '8%'}
          </div>
          <div className="text-xs text-gray-600">CO₂ Reduction</div>
        </div>
      </div>
    </motion.div>
  );
}

export default ModeToggle;
