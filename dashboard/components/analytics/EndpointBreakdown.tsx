'use client';

import React from 'react';
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Tooltip,
  Legend,
} from 'recharts';

interface EndpointData {
  endpoint: string;
  requests: number;
  cost: number;
  percentage: number;
}

interface EndpointBreakdownProps {
  data: EndpointData[];
  height?: number;
}

const COLORS = [
  '#3b82f6', // blue
  '#10b981', // green
  '#f59e0b', // amber
  '#ef4444', // red
  '#8b5cf6', // purple
  '#ec4899', // pink
  '#06b6d4', // cyan
  '#f97316', // orange
];

export default function EndpointBreakdown({
  data,
  height = 300,
}: EndpointBreakdownProps) {
  const chartData = data.map((item) => ({
    name: item.endpoint,
    value: item.requests,
    cost: item.cost,
  }));

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0];
      return (
        <div className="bg-white p-3 border border-gray-200 rounded-lg shadow-lg">
          <p className="font-semibold text-gray-900">{data.name}</p>
          <p className="text-sm text-gray-600">
            Requests: {data.value.toLocaleString()}
          </p>
          <p className="text-sm text-gray-600">
            Cost: ${data.payload.cost.toFixed(4)}
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <div>
      <ResponsiveContainer width="100%" height={height}>
        <PieChart>
          <Pie
            data={chartData}
            cx="50%"
            cy="50%"
            labelLine={false}
            label={({ name, percent }) =>
              `${name}: ${(percent * 100).toFixed(0)}%`
            }
            outerRadius={80}
            fill="#8884d8"
            dataKey="value"
          >
            {chartData.map((entry, index) => (
              <Cell
                key={`cell-${index}`}
                fill={COLORS[index % COLORS.length]}
              />
            ))}
          </Pie>
          <Tooltip content={<CustomTooltip />} />
        </PieChart>
      </ResponsiveContainer>

      <div className="mt-4 space-y-2">
        {data.map((item, index) => (
          <div
            key={item.endpoint}
            className="flex items-center justify-between p-2 bg-gray-50 rounded"
          >
            <div className="flex items-center space-x-2">
              <div
                className="w-3 h-3 rounded-full"
                style={{ backgroundColor: COLORS[index % COLORS.length] }}
              />
              <span className="text-sm font-medium text-gray-700">
                {item.endpoint}
              </span>
            </div>
            <div className="flex space-x-4 text-sm text-gray-600">
              <span>{item.requests.toLocaleString()} requests</span>
              <span>${item.cost.toFixed(4)}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
