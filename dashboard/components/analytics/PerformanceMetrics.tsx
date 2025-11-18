'use client';

import React from 'react';
import {
  ComposedChart,
  Line,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

interface PerformanceData {
  timestamp: string;
  requests: number;
  avg_latency: number;
  p95_latency: number;
  p99_latency: number;
  error_rate: number;
}

interface PerformanceMetricsProps {
  data: PerformanceData[];
  height?: number;
}

export default function PerformanceMetrics({
  data,
  height = 300,
}: PerformanceMetricsProps) {
  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
    });
  };

  const chartData = data.map((point) => ({
    ...point,
    timestamp: formatTimestamp(point.timestamp),
    error_rate: point.error_rate * 100, // Convert to percentage
  }));

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white p-3 border border-gray-200 rounded-lg shadow-lg">
          <p className="font-semibold text-gray-900 mb-2">{label}</p>
          {payload.map((entry: any, index: number) => (
            <p key={index} className="text-sm" style={{ color: entry.color }}>
              {entry.name}:{' '}
              {entry.name === 'Error Rate'
                ? `${entry.value.toFixed(2)}%`
                : entry.name === 'Requests'
                ? entry.value.toLocaleString()
                : `${entry.value.toFixed(0)}ms`}
            </p>
          ))}
        </div>
      );
    }
    return null;
  };

  return (
    <ResponsiveContainer width="100%" height={height}>
      <ComposedChart data={chartData}>
        <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
        <XAxis dataKey="timestamp" stroke="#6b7280" style={{ fontSize: '12px' }} />
        <YAxis
          yAxisId="left"
          stroke="#6b7280"
          style={{ fontSize: '12px' }}
          label={{ value: 'Latency (ms)', angle: -90, position: 'insideLeft' }}
        />
        <YAxis
          yAxisId="right"
          orientation="right"
          stroke="#6b7280"
          style={{ fontSize: '12px' }}
          label={{ value: 'Requests / Error %', angle: 90, position: 'insideRight' }}
        />
        <Tooltip content={<CustomTooltip />} />
        <Legend />

        {/* Latency lines */}
        <Line
          yAxisId="left"
          type="monotone"
          dataKey="avg_latency"
          stroke="#3b82f6"
          strokeWidth={2}
          name="Avg Latency"
          dot={false}
        />
        <Line
          yAxisId="left"
          type="monotone"
          dataKey="p95_latency"
          stroke="#f59e0b"
          strokeWidth={2}
          name="P95 Latency"
          dot={false}
        />
        <Line
          yAxisId="left"
          type="monotone"
          dataKey="p99_latency"
          stroke="#ef4444"
          strokeWidth={2}
          name="P99 Latency"
          dot={false}
        />

        {/* Request volume bars */}
        <Bar
          yAxisId="right"
          dataKey="requests"
          fill="#10b981"
          opacity={0.3}
          name="Requests"
        />

        {/* Error rate line */}
        <Line
          yAxisId="right"
          type="monotone"
          dataKey="error_rate"
          stroke="#dc2626"
          strokeWidth={2}
          name="Error Rate"
          dot={false}
        />
      </ComposedChart>
    </ResponsiveContainer>
  );
}
