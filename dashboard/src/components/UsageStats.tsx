'use client';

import { useState, useEffect } from 'react';

interface UsageStatsProps {
  apiKey: string;
}

export function UsageStats({ apiKey }: UsageStatsProps) {
  const [stats, setStats] = useState<any>(null);
  const [period, setPeriod] = useState('30d');

  useEffect(() => {
    fetchUsageStats();
  }, [apiKey, period]);

  const fetchUsageStats = async () => {
    try {
      const response = await fetch(`/api/v1/manage/usage?period=${period}`, {
        headers: { 'Authorization': `Bearer ${apiKey}` },
      });
      if (response.ok) {
        const data = await response.json();
        setStats(data);
      }
    } catch (error) {
      console.error('Failed to fetch usage stats:', error);
    }
  };

  if (!stats) {
    return <div className="bg-white rounded-lg shadow p-6">Loading...</div>;
  }

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-xl font-bold">Usage Statistics</h2>
        <select
          value={period}
          onChange={(e) => setPeriod(e.target.value)}
          className="px-4 py-2 border rounded-lg"
        >
          <option value="24h">Last 24 Hours</option>
          <option value="7d">Last 7 Days</option>
          <option value="30d">Last 30 Days</option>
          <option value="90d">Last 90 Days</option>
        </select>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div className="p-4 bg-blue-50 rounded-lg">
          <p className="text-sm text-gray-600 mb-1">Total Requests</p>
          <p className="text-3xl font-bold text-blue-600">{stats.total_requests.toLocaleString()}</p>
        </div>
        <div className="p-4 bg-green-50 rounded-lg">
          <p className="text-sm text-gray-600 mb-1">Total Cost</p>
          <p className="text-3xl font-bold text-green-600">${stats.total_cost.toFixed(2)}</p>
        </div>
        <div className="p-4 bg-purple-50 rounded-lg">
          <p className="text-sm text-gray-600 mb-1">Total Tokens</p>
          <p className="text-3xl font-bold text-purple-600">{stats.total_tokens.toLocaleString()}</p>
        </div>
      </div>

      <div>
        <h3 className="font-semibold mb-3">Usage by Endpoint</h3>
        <div className="space-y-2">
          {Object.entries(stats.by_endpoint || {}).map(([endpoint, data]: [string, any]) => (
            <div key={endpoint} className="p-3 border rounded-lg">
              <div className="flex justify-between items-center">
                <span className="font-medium text-sm">{endpoint}</span>
                <span className="text-sm text-gray-600">${data.cost.toFixed(4)}</span>
              </div>
              <div className="flex justify-between text-xs text-gray-500 mt-1">
                <span>{data.requests} requests</span>
                <span>{data.tokens} tokens</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
