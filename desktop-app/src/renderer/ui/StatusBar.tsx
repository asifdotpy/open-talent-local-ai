import React from 'react';
import type { ServiceHealth } from '../../services/integration-service-client';

interface Props {
  services: ServiceHealth[];
  integrationStatus: 'online' | 'offline' | 'degraded';
}

export const StatusBar: React.FC<Props> = ({ services, integrationStatus }) => {
  return (
    <div className="status-bar">
      <div className={`status-pill ${integrationStatus}`}>Gateway: {integrationStatus}</div>
      <div className="status-grid">
        {services.map((s) => (
          <div key={s.name} className={`status-card ${s.status}`}>
            <div className="status-card-header">
              <span className={`dot ${s.status}`} />
              <span className="name">{s.name}</span>
            </div>
            {typeof s.latencyMs === 'number' && (
              <div className="latency">{s.latencyMs} ms</div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default StatusBar;
