'use client';

import React, { useState, useEffect, useRef } from 'react';
import { Activity, TrendingUp, TrendingDown, Minus } from 'lucide-react';

interface MetricData {
  value: number;
  change: number;
  trend: 'up' | 'down' | 'stable';
}

interface RealTimeMetricsProps {
  apiKey: string;
  wsUrl?: string;
}

export default function RealTimeMetrics({
  apiKey,
  wsUrl = 'ws://localhost:8000/ws',
}: RealTimeMetricsProps) {
  const [requests, setRequests] = useState<MetricData>({
    value: 0,
    change: 0,
    trend: 'stable',
  });
  const [cost, setCost] = useState<MetricData>({
    value: 0,
    change: 0,
    trend: 'stable',
  });
  const [latency, setLatency] = useState<MetricData>({
    value: 0,
    change: 0,
    trend: 'stable',
  });
  const [connected, setConnected] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    const connectWebSocket = () => {
      const ws = new WebSocket(`${wsUrl}?api_key=${apiKey}`);

      ws.onopen = () => {
        console.log('WebSocket connected');
        setConnected(true);

        // Subscribe to usage updates
        ws.send(
          JSON.stringify({
            type: 'subscribe',
            events: ['usage_update'],
          })
        );
      };

      ws.onmessage = (event) => {
        const message = JSON.parse(event.data);

        if (message.type === 'usage_update') {
          const data = message.data;

          // Update requests metric
          if (data.requests !== undefined) {
            setRequests((prev) => ({
              value: data.requests,
              change: data.requests - prev.value,
              trend:
                data.requests > prev.value
                  ? 'up'
                  : data.requests < prev.value
                  ? 'down'
                  : 'stable',
            }));
          }

          // Update cost metric
          if (data.cost !== undefined) {
            setCost((prev) => ({
              value: data.cost,
              change: data.cost - prev.value,
              trend:
                data.cost > prev.value
                  ? 'up'
                  : data.cost < prev.value
                  ? 'down'
                  : 'stable',
            }));
          }

          // Update latency metric
          if (data.avg_latency !== undefined) {
            setLatency((prev) => ({
              value: data.avg_latency,
              change: data.avg_latency - prev.value,
              trend:
                data.avg_latency > prev.value
                  ? 'up'
                  : data.avg_latency < prev.value
                  ? 'down'
                  : 'stable',
            }));
          }
        }
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        setConnected(false);
      };

      ws.onclose = () => {
        console.log('WebSocket closed');
        setConnected(false);

        // Reconnect after 3 seconds
        setTimeout(connectWebSocket, 3000);
      };

      wsRef.current = ws;
    };

    connectWebSocket();

    // Cleanup on unmount
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [apiKey, wsUrl]);

  const getTrendIcon = (trend: 'up' | 'down' | 'stable') => {
    switch (trend) {
      case 'up':
        return <TrendingUp className="w-4 h-4 text-green-500" />;
      case 'down':
        return <TrendingDown className="w-4 h-4 text-red-500" />;
      default:
        return <Minus className="w-4 h-4 text-gray-400" />;
    }
  };

  const formatChange = (change: number, isPercent = false) => {
    const sign = change > 0 ? '+' : '';
    return isPercent
      ? `${sign}${change.toFixed(1)}%`
      : `${sign}${change.toFixed(2)}`;
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">
          Real-Time Metrics
        </h3>
        <div className="flex items-center space-x-2">
          <div
            className={`w-2 h-2 rounded-full ${
              connected ? 'bg-green-500' : 'bg-red-500'
            }`}
          />
          <span className="text-sm text-gray-600">
            {connected ? 'Connected' : 'Disconnected'}
          </span>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Requests */}
        <div className="bg-white p-4 rounded-lg border border-gray-200 shadow-sm">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-600">
              Requests/min
            </span>
            {getTrendIcon(requests.trend)}
          </div>
          <div className="flex items-baseline space-x-2">
            <span className="text-2xl font-bold text-gray-900">
              {requests.value.toLocaleString()}
            </span>
            {requests.change !== 0 && (
              <span
                className={`text-sm ${
                  requests.trend === 'up'
                    ? 'text-green-600'
                    : requests.trend === 'down'
                    ? 'text-red-600'
                    : 'text-gray-500'
                }`}
              >
                {formatChange(requests.change)}
              </span>
            )}
          </div>
          <div className="mt-1 text-xs text-gray-500">
            Total API requests per minute
          </div>
        </div>

        {/* Cost */}
        <div className="bg-white p-4 rounded-lg border border-gray-200 shadow-sm">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-600">
              Cost/hour
            </span>
            {getTrendIcon(cost.trend)}
          </div>
          <div className="flex items-baseline space-x-2">
            <span className="text-2xl font-bold text-gray-900">
              ${cost.value.toFixed(4)}
            </span>
            {cost.change !== 0 && (
              <span
                className={`text-sm ${
                  cost.trend === 'up'
                    ? 'text-green-600'
                    : cost.trend === 'down'
                    ? 'text-red-600'
                    : 'text-gray-500'
                }`}
              >
                {formatChange(cost.change)}
              </span>
            )}
          </div>
          <div className="mt-1 text-xs text-gray-500">
            Current spending rate
          </div>
        </div>

        {/* Latency */}
        <div className="bg-white p-4 rounded-lg border border-gray-200 shadow-sm">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-600">
              Avg Latency
            </span>
            {getTrendIcon(latency.trend)}
          </div>
          <div className="flex items-baseline space-x-2">
            <span className="text-2xl font-bold text-gray-900">
              {latency.value.toFixed(0)}
            </span>
            <span className="text-sm text-gray-600">ms</span>
            {latency.change !== 0 && (
              <span
                className={`text-sm ${
                  latency.trend === 'down'
                    ? 'text-green-600'
                    : latency.trend === 'up'
                    ? 'text-red-600'
                    : 'text-gray-500'
                }`}
              >
                {formatChange(latency.change)}
              </span>
            )}
          </div>
          <div className="mt-1 text-xs text-gray-500">
            Average response time
          </div>
        </div>
      </div>

      {!connected && (
        <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
          <p className="text-sm text-yellow-800">
            Attempting to reconnect to real-time data stream...
          </p>
        </div>
      )}
    </div>
  );
}
