import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer
} from 'recharts';
import { 
  FiTrendingUp, 
  FiTrendingDown, 
  FiBarChart,
  FiClock,
  FiWind,
  FiTruck
} from 'react-icons/fi';
import axios from 'axios';

const AnalyticsPanel = () => {
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [timeRange, setTimeRange] = useState('24h');

  useEffect(() => {
    fetchAnalytics();
    const interval = setInterval(fetchAnalytics, 30000); // Update every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchAnalytics = async () => {
    try {
      const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:5050';
      const response = await axios.get(`${apiUrl}/api/analytics`, {
        timeout: 10000 // 10 second timeout
      });
      setAnalytics(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Failed to fetch analytics:', error);
      // Set fallback data structure
      setAnalytics({
        hourly_traffic: [],
        co2_trends: [],
        congestion_hotspots: []
      });
      setLoading(false);
    }
  };

  const getCO2TrendData = () => {
    if (!analytics?.co2_trends || !Array.isArray(analytics.co2_trends)) return [];
    return analytics.co2_trends.map(item => ({
      date: new Date(item.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
      co2_saved: item.co2_saved || 0
    }));
  };

  const getHourlyTrafficData = () => {
    if (!analytics?.hourly_traffic || !Array.isArray(analytics.hourly_traffic)) return [];
    return analytics.hourly_traffic.slice(-12).map(item => ({
      hour: `${item.hour}:00`,
      vehicles: item.vehicles || 0,
      co2_saved: item.co2_saved || 0
    }));
  };

  const getCongestionData = () => {
    if (!analytics?.congestion_hotspots || !Array.isArray(analytics.congestion_hotspots)) return [];
    return analytics.congestion_hotspots.map(item => ({
      location: item.location ? item.location.split(' ')[0] : 'Unknown', // Get first word for better display
      congestion: item.congestion_level || 0,
      trend: item.trend || 'stable'
    }));
  };

  const getTrendIcon = (trend) => {
    switch (trend) {
      case 'increasing': return <FiTrendingUp className="w-4 h-4 text-red-500" />;
      case 'decreasing': return <FiTrendingDown className="w-4 h-4 text-green-500" />;
      default: return <FiBarChart className="w-4 h-4 text-gray-500" />;
    }
  };


  if (loading) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto mb-2"></div>
          <p className="text-gray-500">Loading analytics...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="p-6 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-semibold text-gray-800">Analytics Dashboard</h2>
            <p className="text-sm text-gray-600">Traffic patterns and environmental impact</p>
          </div>
          <div className="flex space-x-2">
            {['24h', '7d', '30d'].map((range) => (
              <button
                key={range}
                onClick={() => setTimeRange(range)}
                className={`px-3 py-1 rounded-lg text-sm font-medium transition-colors ${
                  timeRange === range
                    ? 'bg-blue-500 text-white'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
              >
                {range}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Charts Grid */}
      <div className="flex-1 p-6 overflow-y-auto">
        <div className="grid grid-cols-1 gap-6">
          {/* CO2 Savings Trend */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="bg-white rounded-lg p-4 border border-gray-200"
          >
            <div className="flex items-center space-x-2 mb-4">
              <FiWind className="w-5 h-5 text-green-500" />
              <h3 className="text-lg font-semibold text-gray-800">CO₂ Savings Trend</h3>
            </div>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={getCO2TrendData()}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                  <XAxis 
                    dataKey="date" 
                    stroke="#6b7280"
                    fontSize={12}
                  />
                  <YAxis 
                    stroke="#6b7280"
                    fontSize={12}
                  />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: 'white',
                      border: '1px solid #e5e7eb',
                      borderRadius: '8px',
                      boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
                    }}
                  />
                  <Line
                    type="monotone"
                    dataKey="co2_saved"
                    stroke="#22c55e"
                    strokeWidth={3}
                    dot={{ fill: '#22c55e', strokeWidth: 2, r: 4 }}
                    activeDot={{ r: 6, stroke: '#22c55e', strokeWidth: 2 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </motion.div>

          {/* Hourly Traffic Volume */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.1 }}
            className="bg-white rounded-lg p-4 border border-gray-200"
          >
            <div className="flex items-center space-x-2 mb-4">
              <FiTruck className="w-5 h-5 text-blue-500" />
              <h3 className="text-lg font-semibold text-gray-800">Hourly Traffic Volume</h3>
            </div>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={getHourlyTrafficData()}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                  <XAxis 
                    dataKey="hour" 
                    stroke="#6b7280"
                    fontSize={12}
                  />
                  <YAxis 
                    stroke="#6b7280"
                    fontSize={12}
                  />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: 'white',
                      border: '1px solid #e5e7eb',
                      borderRadius: '8px',
                      boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
                    }}
                  />
                  <Bar dataKey="vehicles" fill="#3b82f6" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </motion.div>

          {/* Congestion Hotspots */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="bg-white rounded-lg p-4 border border-gray-200"
          >
            <div className="flex items-center space-x-2 mb-4">
              <FiClock className="w-5 h-5 text-orange-500" />
              <h3 className="text-lg font-semibold text-gray-800">Congestion Hotspots</h3>
            </div>
            <div className="space-y-3">
              {getCongestionData().map((item, index) => (
                <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div className="flex items-center space-x-3">
                    <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                      <span className="text-sm font-semibold text-blue-600">{index + 1}</span>
                    </div>
                    <div>
                      <p className="font-medium text-gray-800">{item.location}</p>
                      <div className="flex items-center space-x-2">
                        <div className="w-16 bg-gray-200 rounded-full h-2">
                          <div
                            className={`h-2 rounded-full ${
                              item.congestion > 80 ? 'bg-red-500' :
                              item.congestion > 60 ? 'bg-yellow-500' : 'bg-green-500'
                            }`}
                            style={{ width: `${item.congestion}%` }}
                          ></div>
                        </div>
                        <span className="text-sm text-gray-600">{item.congestion}%</span>
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center space-x-1">
                    {getTrendIcon(item.trend)}
                  </div>
                </div>
              ))}
            </div>
          </motion.div>

          {/* Performance Metrics */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.3 }}
            className="grid grid-cols-2 gap-4"
          >
            <div className="bg-white rounded-lg p-4 border border-gray-200">
              <div className="flex items-center space-x-2 mb-2">
                <FiTrendingUp className="w-4 h-4 text-green-500" />
                <h4 className="text-sm font-medium text-gray-800">Efficiency</h4>
              </div>
              <div className="text-2xl font-bold text-gray-900">98.5%</div>
              <div className="text-xs text-green-600">+2.3% from last week</div>
            </div>
            
            <div className="bg-white rounded-lg p-4 border border-gray-200">
              <div className="flex items-center space-x-2 mb-2">
                <FiWind className="w-4 h-4 text-green-500" />
                <h4 className="text-sm font-medium text-gray-800">CO₂ Reduction</h4>
              </div>
              <div className="text-2xl font-bold text-gray-900">12.4%</div>
              <div className="text-xs text-green-600">+1.8% from last week</div>
            </div>
          </motion.div>
        </div>
      </div>
    </div>
  );
};

export default AnalyticsPanel;
