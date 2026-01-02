import { useEffect, useState } from 'react';
import { Activity, AlertCircle, CheckCircle, Server } from 'lucide-react';
import integrationGatewayAPI from '../services/integrationGatewayAPI';

interface ServiceStatusData {
  status: 'online' | 'degraded' | 'offline';
  onlineCount: number;
  totalCount: number;
  timestamp: string;
  services: Record<string, boolean>;
}

export const ServiceStatus = () => {
  const [statusData, setStatusData] = useState<ServiceStatusData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [lastChecked, setLastChecked] = useState<Date | null>(null);

  const fetchStatus = async () => {
    try {
      setIsLoading(true);
      const response = await integrationGatewayAPI.health.getSystemStatus();

      // Parse the response to get service counts
      const services = response.services || {};
      const onlineCount = Object.values(services).filter(s => s === true).length;
      const totalCount = Object.keys(services).length;

      const status = onlineCount >= 6 ? 'online' : onlineCount >= 3 ? 'degraded' : 'offline';

      setStatusData({
        status,
        onlineCount,
        totalCount,
        timestamp: response.timestamp,
        services
      });
      setLastChecked(new Date());
    } catch (error) {
      console.error('Failed to fetch service status:', error);
      setStatusData({
        status: 'offline',
        onlineCount: 0,
        totalCount: 0,
        timestamp: new Date().toISOString(),
        services: {}
      });
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchStatus();
    const interval = setInterval(fetchStatus, 30000); // Check every 30 seconds
    return () => clearInterval(interval);
  }, []);

  if (isLoading || !statusData) {
    return (
      <div className="flex items-center space-x-2">
        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
        <span className="text-sm text-gray-600">Checking services...</span>
      </div>
    );
  }

  const statusConfig = {
    online: {
      icon: CheckCircle,
      color: 'text-green-600',
      bgColor: 'bg-green-50',
      label: 'All Systems Operational'
    },
    degraded: {
      icon: AlertCircle,
      color: 'text-yellow-600',
      bgColor: 'bg-yellow-50',
      label: 'Degraded Service'
    },
    offline: {
      icon: AlertCircle,
      color: 'text-red-600',
      bgColor: 'bg-red-50',
      label: 'Service Unavailable'
    }
  };

  const config = statusConfig[statusData.status];
  const StatusIcon = config.icon;

  return (
    <div className="flex items-center space-x-4">
      {/* Status Badge */}
      <div className={`flex items-center space-x-2 px-3 py-2 rounded-full ${config.bgColor}`}>
        <StatusIcon className={`h-4 w-4 ${config.color}`} />
        <span className={`text-sm font-medium ${config.color}`}>
          {config.label}
        </span>
      </div>

      {/* Service Count */}
      <div className="flex items-center space-x-1 text-sm text-gray-600">
        <Server className="h-4 w-4" />
        <span>{statusData.onlineCount}/{statusData.totalCount} services</span>
      </div>

      {/* Last Checked */}
      {lastChecked && (
        <div className="text-xs text-gray-500">
          Checked {Math.round((Date.now() - lastChecked.getTime()) / 1000)}s ago
        </div>
      )}

      {/* Refresh Button */}
      <button
        onClick={fetchStatus}
        disabled={isLoading}
        className="ml-2 p-1 rounded hover:bg-gray-200 transition-colors disabled:opacity-50"
        title="Refresh service status"
      >
        <Activity className="h-4 w-4 text-gray-600" />
      </button>
    </div>
  );
};
