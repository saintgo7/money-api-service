'use client';

import React from 'react';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

interface UsageDataPoint {
  timestamp: string;
  requests: number;
  cost: number;
  tokens?: number;
}

interface UsageChartProps {
  data: UsageDataPoint[];
  type?: 'line' | 'area' | 'bar';
  metric?: 'requests' | 'cost' | 'tokens';
  height?: number;
}

export default function UsageChart({
  data,
  type = 'area',
  metric = 'requests',
  height = 300,
}: UsageChartProps) {
  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
    });
  };

  const formatValue = (value: number) => {
    if (metric === 'cost') {
      return `$${value.toFixed(4)}`;
    }
    if (metric === 'tokens') {
      return value.toLocaleString();
    }
    return value.toString();
  };

  const getMetricLabel = () => {
    switch (metric) {
      case 'requests':
        return 'Requests';
      case 'cost':
        return 'Cost ($)';
      case 'tokens':
        return 'Tokens';
      default:
        return metric;
    }
  };

  const getMetricColor = () => {
    switch (metric) {
      case 'requests':
        return '#3b82f6'; // blue
      case 'cost':
        return '#10b981'; // green
      case 'tokens':
        return '#8b5cf6'; // purple
      default:
        return '#3b82f6';
    }
  };

  const chartData = data.map((point) => ({
    ...point,
    timestamp: formatTimestamp(point.timestamp),
  }));

  if (type === 'line') {
    return (
      <ResponsiveContainer width="100%" height={height}>
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis
            dataKey="timestamp"
            stroke="#6b7280"
            style={{ fontSize: '12px' }}
          />
          <YAxis
            stroke="#6b7280"
            style={{ fontSize: '12px' }}
            tickFormatter={formatValue}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: '#fff',
              border: '1px solid #e5e7eb',
              borderRadius: '8px',
            }}
            formatter={(value: number) => [formatValue(value), getMetricLabel()]}
          />
          <Legend />
          <Line
            type="monotone"
            dataKey={metric}
            stroke={getMetricColor()}
            strokeWidth={2}
            dot={{ fill: getMetricColor(), r: 4 }}
            name={getMetricLabel()}
          />
        </LineChart>
      </ResponsiveContainer>
    );
  }

  if (type === 'area') {
    return (
      <ResponsiveContainer width="100%" height={height}>
        <AreaChart data={chartData}>
          <defs>
            <linearGradient id="colorMetric" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor={getMetricColor()} stopOpacity={0.8} />
              <stop offset="95%" stopColor={getMetricColor()} stopOpacity={0.1} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis
            dataKey="timestamp"
            stroke="#6b7280"
            style={{ fontSize: '12px' }}
          />
          <YAxis
            stroke="#6b7280"
            style={{ fontSize: '12px' }}
            tickFormatter={formatValue}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: '#fff',
              border: '1px solid #e5e7eb',
              borderRadius: '8px',
            }}
            formatter={(value: number) => [formatValue(value), getMetricLabel()]}
          />
          <Area
            type="monotone"
            dataKey={metric}
            stroke={getMetricColor()}
            strokeWidth={2}
            fillOpacity={1}
            fill="url(#colorMetric)"
            name={getMetricLabel()}
          />
        </AreaChart>
      </ResponsiveContainer>
    );
  }

  return (
    <ResponsiveContainer width="100%" height={height}>
      <BarChart data={chartData}>
        <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
        <XAxis
          dataKey="timestamp"
          stroke="#6b7280"
          style={{ fontSize: '12px' }}
        />
        <YAxis
          stroke="#6b7280"
          style={{ fontSize: '12px' }}
          tickFormatter={formatValue}
        />
        <Tooltip
          contentStyle={{
            backgroundColor: '#fff',
            border: '1px solid #e5e7eb',
            borderRadius: '8px',
          }}
          formatter={(value: number) => [formatValue(value), getMetricLabel()]}
        />
        <Bar
          dataKey={metric}
          fill={getMetricColor()}
          radius={[4, 4, 0, 0]}
          name={getMetricLabel()}
        />
      </BarChart>
    </ResponsiveContainer>
  );
}
