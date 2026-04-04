import React, { useState, useEffect, useRef } from 'react';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, ReferenceLine
} from 'recharts';

const KPI_COLORS = {
  revenue_per_hour: '#8b5cf6',
  active_users:     '#06b6d4',
  conversion_rate:  '#10b981',
  error_rate:       '#ef4444',
  avg_response_ms:  '#f59e0b',
  orders_per_min:   '#ec4899',
};

const KPI_LABELS = {
  revenue_per_hour: 'Revenue / Hour',
  active_users:     'Active Users',
  conversion_rate:  'Conversion Rate',
  error_rate:       'Error Rate',
  avg_response_ms:  'Avg Response Time',
  orders_per_min:   'Orders / Min',
};

function MetricCard({ metric, history }) {
  const color = KPI_COLORS[metric.name] || '#8b5cf6';
  const label = KPI_LABELS[metric.name] || metric.name;
  const pctChange = metric.baseline
    ? ((metric.value - metric.baseline) / metric.baseline * 100).toFixed(1)
    : 0;
  const isUp = pctChange >= 0;
  const isError = metric.name === 'error_rate' || metric.name === 'avg_response_ms';

  return (
    <div style={{
      background: metric.is_anomaly ? 'rgba(239,68,68,0.1)' : 'rgba(26,26,46,0.6)',
      border: `1px solid ${metric.is_anomaly ? '#ef4444' : color}33`,
      borderRadius: 12,
      padding: '1.2rem',
      backdropFilter: 'blur(10px)',
      transition: 'all 0.3s ease',
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <p style={{ color: '#94a3b8', fontSize: 12, margin: 0 }}>{label}</p>
          <h2 style={{ color: '#fff', fontSize: 28, margin: '4px 0', fontWeight: 700 }}>
            {metric.unit === '$' ? '$' : ''}
            {metric.value > 1 ? Math.round(metric.value).toLocaleString() : metric.value.toFixed(4)}
            {metric.unit !== '$' ? metric.unit : ''}
          </h2>
          <span style={{
            color: (isUp && !isError) || (!isUp && isError) ? '#10b981' : '#ef4444',
            fontSize: 13, fontWeight: 600
          }}>
            {isUp ? '▲' : '▼'} {Math.abs(pctChange)}% vs baseline
          </span>
        </div>
        {metric.is_anomaly && (
          <span style={{
            background: '#ef444422', color: '#ef4444',
            padding: '2px 8px', borderRadius: 20, fontSize: 11, fontWeight: 700
          }}>
            ⚠ ANOMALY
          </span>
        )}
      </div>

      {/* Sparkline */}
      <div style={{ marginTop: 12, height: 50 }}>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={history.map((v, i) => ({ i, v }))}>
            <Line type="monotone" dataKey="v" stroke={color} dot={false} strokeWidth={2} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

function AlertBanner({ alerts }) {
  if (!alerts.length) return null;
  return (
    <div style={{
      background: 'rgba(239,68,68,0.15)', border: '1px solid #ef4444',
      borderRadius: 8, padding: '0.8rem 1.2rem', marginBottom: '1rem'
    }}>
      <strong style={{ color: '#ef4444' }}>⚠ Active Alerts ({alerts.length})</strong>
      {alerts.map((a, i) => (
        <div key={i} style={{ color: '#fca5a5', fontSize: 13, marginTop: 4 }}>
          {a.message} — severity: <strong>{a.severity}</strong>
        </div>
      ))}
    </div>
  );
}

export default function Dashboard() {
  const [metrics, setMetrics] = useState({});
  const [alerts, setAlerts] = useState([]);
  const [connected, setConnected] = useState(false);
  const historyRef = useRef({});
  const wsRef = useRef(null);

  useEffect(() => {
    const ws = new WebSocket('ws://localhost:8000/ws/metrics');
    wsRef.current = ws;

    ws.onopen = () => setConnected(true);
    ws.onclose = () => setConnected(false);

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);

      // Update history
      data.metrics.forEach(m => {
        if (!historyRef.current[m.name]) historyRef.current[m.name] = [];
        historyRef.current[m.name].push(m.value);
        if (historyRef.current[m.name].length > 60) historyRef.current[m.name].shift();
      });

      const metricsMap = {};
      data.metrics.forEach(m => { metricsMap[m.name] = m; });
      setMetrics(metricsMap);
      setAlerts(data.alerts || []);
    };

    return () => ws.close();
  }, []);

  return (
    <div style={{
      minHeight: '100vh', background: '#0f0f23', color: '#fff',
      fontFamily: 'Inter, sans-serif', padding: '2rem'
    }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
        <div>
          <h1 style={{ margin: 0, fontSize: 24, fontWeight: 700 }}>📊 Real-Time KPI Monitor</h1>
          <p style={{ color: '#94a3b8', margin: '4px 0 0', fontSize: 13 }}>
            Live metrics — updates every second
          </p>
        </div>
        <div style={{
          display: 'flex', alignItems: 'center', gap: 8,
          background: connected ? 'rgba(16,185,129,0.1)' : 'rgba(239,68,68,0.1)',
          border: `1px solid ${connected ? '#10b981' : '#ef4444'}`,
          borderRadius: 20, padding: '4px 12px', fontSize: 13
        }}>
          <span style={{ width: 8, height: 8, borderRadius: '50%', background: connected ? '#10b981' : '#ef4444', display: 'inline-block' }} />
          {connected ? 'Connected' : 'Disconnected'}
        </div>
      </div>

      <AlertBanner alerts={alerts} />

      {/* KPI Grid */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))',
        gap: '1rem'
      }}>
        {Object.values(metrics).map(metric => (
          <MetricCard
            key={metric.name}
            metric={metric}
            history={historyRef.current[metric.name] || []}
          />
        ))}
      </div>

      {!Object.keys(metrics).length && (
        <div style={{ textAlign: 'center', color: '#94a3b8', marginTop: '4rem' }}>
          <p style={{ fontSize: 18 }}>Connecting to metrics stream...</p>
        </div>
      )}
    </div>
  );
}