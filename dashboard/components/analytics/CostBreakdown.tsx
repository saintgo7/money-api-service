'use client';

import React from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

interface CostData {
  category: string;
  text: number;
  image: number;
  audio: number;
  document: number;
  total: number;
}

interface CostBreakdownProps {
  data: CostData[];
  height?: number;
}

export default function CostBreakdown({ data, height = 300 }: CostBreakdownProps) {
  const formatCost = (value: number) => `$${value.toFixed(4)}`;

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      const total = payload.reduce(
        (sum: number, entry: any) => sum + entry.value,
        0
      );

      return (
        <div className="bg-white p-3 border border-gray-200 rounded-lg shadow-lg">
          <p className="font-semibold text-gray-900 mb-2">{label}</p>
          {payload.map((entry: any, index: number) => (
            <p key={index} className="text-sm" style={{ color: entry.color }}>
              {entry.name}: {formatCost(entry.value)}
            </p>
          ))}
          <p className="text-sm font-semibold text-gray-900 mt-2 pt-2 border-t border-gray-200">
            Total: {formatCost(total)}
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <ResponsiveContainer width="100%" height={height}>
      <BarChart data={data}>
        <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
        <XAxis dataKey="category" stroke="#6b7280" style={{ fontSize: '12px' }} />
        <YAxis
          stroke="#6b7280"
          style={{ fontSize: '12px' }}
          tickFormatter={formatCost}
        />
        <Tooltip content={<CustomTooltip />} />
        <Legend />
        <Bar dataKey="text" stackId="a" fill="#3b82f6" name="Text API" />
        <Bar dataKey="image" stackId="a" fill="#10b981" name="Image API" />
        <Bar dataKey="audio" stackId="a" fill="#f59e0b" name="Audio API" />
        <Bar
          dataKey="document"
          stackId="a"
          fill="#8b5cf6"
          name="Document API"
        />
      </BarChart>
    </ResponsiveContainer>
  );
}
