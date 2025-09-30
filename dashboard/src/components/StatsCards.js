import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  FiTruck, 
  FiWind, 
  FiClock, 
  FiTrendingUp,
  FiTrendingDown,
  FiMinus
} from 'react-icons/fi';
import { useSocket } from '../context/SocketContext';

const StatCard = ({ icon: Icon, title, value, subtitle, trend, color, delay = 0 }) => {
  const getTrendIcon = () => {
    switch (trend?.direction) {
      case 'up': return <FiTrendingUp className="w-4 h-4 text-green-500" />;
      case 'down': return <FiTrendingDown className="w-4 h-4 text-red-500" />;
      default: return <FiMinus className="w-4 h-4 text-gray-400" />;
    }
  };

  const getTrendColor = () => {
    switch (trend?.direction) {
      case 'up': return 'text-green-600';
      case 'down': return 'text-red-600';
      default: return 'text-gray-500';
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay }}
      className={`bg-white rounded-xl shadow-lg p-6 border-l-4 ${color}`}
    >
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <div className={`p-3 rounded-lg ${color.replace('border-l-', 'bg-').replace('-500', '-50')}`}>
            <Icon className={`w-6 h-6 ${color.replace('border-l-', 'text-')}`} />
          </div>
          <div>
            <h3 className="text-sm font-medium text-gray-500 uppercase tracking-wide">
              {title}
            </h3>
            <p className="text-2xl font-bold text-gray-900 mt-1">
              {typeof value === 'number' ? value.toLocaleString() : value}
            </p>
            {subtitle && (
              <p className="text-sm text-gray-600 mt-1">{subtitle}</p>
            )}
          </div>
        </div>
        
        {trend && (
          <div className="flex items-center space-x-1">
            {getTrendIcon()}
            <span className={`text-sm font-medium ${getTrendColor()}`}>
              {trend.percentage}%
            </span>
          </div>
        )}
      </div>
    </motion.div>
  );
};

const StatsCards = () => {
  const { stats, signalsVehicleData } = useSocket();
  const [previousStats, setPreviousStats] = useState(null);
  const [trends, setTrends] = useState({
    vehicles: { direction: 'stable', percentage: 0 },
    co2: { direction: 'stable', percentage: 0 },
    waitTime: { direction: 'stable', percentage: 0 }
  });

  // Calculate detailed vehicle statistics
  const getVehicleStats = () => {
    if (signalsVehicleData && signalsVehicleData.system_totals) {
      return {
        total: signalsVehicleData.system_totals.total_vehicles_detected || 0,
        subtitle: `Across ${signalsVehicleData.signals_vehicle_data?.length || 5} signals`,
        isLive: signalsVehicleData.system_totals.cv_active || false
      };
    }
    return {
      total: stats.vehicles_detected || 0,
      subtitle: "Across all signals",
      isLive: false
    };
  };

  const vehicleStats = getVehicleStats();

  // Calculate trends based on previous values
  useEffect(() => {
    if (previousStats && stats) {
      const vehiclesChange = previousStats.vehicles_detected > 0 
        ? ((vehicleStats.total - previousStats.vehicles_detected) / previousStats.vehicles_detected) * 100
        : 0;
      const co2Change = previousStats.co2_saved > 0 
        ? ((stats.co2_saved - previousStats.co2_saved) / previousStats.co2_saved) * 100
        : 0;
      const waitTimeChange = previousStats.avg_wait_time > 0 
        ? ((stats.avg_wait_time - previousStats.avg_wait_time) / previousStats.avg_wait_time) * 100
        : 0;

      setTrends({
        vehicles: {
          direction: vehiclesChange > 2 ? 'up' : vehiclesChange < -2 ? 'down' : 'stable',
          percentage: Math.abs(vehiclesChange).toFixed(1)
        },
        co2: {
          direction: co2Change > 2 ? 'up' : co2Change < -2 ? 'down' : 'stable',
          percentage: Math.abs(co2Change).toFixed(1)
        },
        waitTime: {
          direction: waitTimeChange > 2 ? 'up' : waitTimeChange < -2 ? 'down' : 'stable',
          percentage: Math.abs(waitTimeChange).toFixed(1)
        }
      });
    }

    if (stats) {
      setPreviousStats({ ...stats, vehicles_detected: vehicleStats.total });
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [stats, signalsVehicleData, vehicleStats.total]);

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      <StatCard
        icon={FiTruck}
        title={`Vehicles Detected${vehicleStats.isLive ? ' (Live)' : ''}`}
        value={vehicleStats.total}
        subtitle={vehicleStats.subtitle}
        trend={trends.vehicles}
        color={vehicleStats.isLive ? "border-l-green-500" : "border-l-blue-500"}
        delay={0}
      />
      
      <StatCard
        icon={FiWind}
        title="CO₂ Saved (kg)"
        value={stats.co2_saved || 0}
        subtitle="Environmental impact"
        trend={trends.co2}
        color="border-l-green-500"
        delay={0.1}
      />
      
      <StatCard
        icon={FiClock}
        title="Avg Wait Time"
        value={`${stats.avg_wait_time || 0}s`}
        subtitle="Per intersection"
        trend={trends.waitTime}
        color="border-l-orange-500"
        delay={0.2}
      />
      
      <StatCard
        icon={FiTrendingUp}
        title="System Mode"
        value={stats.mode === 'automation' ? 'AI Control' : 'Manual Override'}
        subtitle={stats.mode === 'automation' ? 'Fully automated' : 'Human controlled'}
        color={stats.mode === 'automation' ? 'border-l-green-500' : 'border-l-yellow-500'}
        delay={0.3}
      />
    </div>
  );
};

export default StatsCards;
