'use client';

import React, { useState, useEffect } from 'react';
import {
  BarChart3,
  TrendingUp,
  Activity,
  DollarSign,
  Clock,
  AlertCircle,
} from 'lucide-react';
import UsageChart from '@/components/analytics/UsageChart';
import EndpointBreakdown from '@/components/analytics/EndpointBreakdown';
import RealTimeMetrics from '@/components/analytics/RealTimeMetrics';
import CostBreakdown from '@/components/analytics/CostBreakdown';
import PerformanceMetrics from '@/components/analytics/PerformanceMetrics';

export default function AnalyticsPage() {
  const [timeRange, setTimeRange] = useState<'24h' | '7d' | '30d'>('7d');
  const [apiKey, setApiKey] = useState<string>('');
  const [usageData, setUsageData] = useState<any[]>([]);
  const [endpointData, setEndpointData] = useState<any[]>([]);
  const [costData, setCostData] = useState<any[]>([]);
  const [performanceData, setPerformanceData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Load API key from localStorage
    const key = localStorage.getItem('api_key');
    if (key) {
      setApiKey(key);
      fetchAnalyticsData(key, timeRange);
    }
  }, [timeRange]);

  const fetchAnalyticsData = async (key: string, range: string) => {
    setLoading(true);
    try {
      const response = await fetch(
        `http://localhost:8000/api/v1/analytics/usage?period=${range}`,
        {
          headers: {
            'X-API-Key': key,
          },
        }
      );

      if (response.ok) {
        const data = await response.json();

        // Transform data for charts
        setUsageData(data.usage_over_time || []);
        setEndpointData(data.endpoint_breakdown || []);
        setCostData(data.cost_breakdown || []);
        setPerformanceData(data.performance_metrics || []);
      }
    } catch (error) {
      console.error('Failed to fetch analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  const summaryStats = [
    {
      title: 'Total Requests',
      value: usageData.reduce((sum, d) => sum + d.requests, 0).toLocaleString(),
      icon: Activity,
      color: 'text-blue-600',
      bgColor: 'bg-blue-100',
    },
    {
      title: 'Total Cost',
      value: `$${usageData
        .reduce((sum, d) => sum + d.cost, 0)
        .toFixed(4)}`,
      icon: DollarSign,
      color: 'text-green-600',
      bgColor: 'bg-green-100',
    },
    {
      title: 'Avg Latency',
      value: `${(
        performanceData.reduce((sum, d) => sum + d.avg_latency, 0) /
        Math.max(performanceData.length, 1)
      ).toFixed(0)}ms`,
      icon: Clock,
      color: 'text-purple-600',
      bgColor: 'bg-purple-100',
    },
    {
      title: 'Error Rate',
      value: `${(
        (performanceData.reduce((sum, d) => sum + d.error_rate, 0) /
          Math.max(performanceData.length, 1)) *
        100
      ).toFixed(2)}%`,
      icon: AlertCircle,
      color: 'text-red-600',
      bgColor: 'bg-red-100',
    },
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 flex items-center">
            <BarChart3 className="w-8 h-8 mr-3 text-blue-600" />
            Advanced Analytics
          </h1>
          <p className="mt-2 text-gray-600">
            Real-time insights and comprehensive metrics for your API usage
          </p>
        </div>

        {/* Time Range Selector */}
        <div className="mb-6 flex space-x-2">
          {(['24h', '7d', '30d'] as const).map((range) => (
            <button
              key={range}
              onClick={() => setTimeRange(range)}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                timeRange === range
                  ? 'bg-blue-600 text-white'
                  : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
              }`}
            >
              {range === '24h'
                ? 'Last 24 Hours'
                : range === '7d'
                ? 'Last 7 Days'
                : 'Last 30 Days'}
            </button>
          ))}
        </div>

        {/* Summary Stats */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          {summaryStats.map((stat) => (
            <div
              key={stat.title}
              className="bg-white p-6 rounded-lg border border-gray-200 shadow-sm"
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">
                    {stat.title}
                  </p>
                  <p className="mt-2 text-3xl font-bold text-gray-900">
                    {stat.value}
                  </p>
                </div>
                <div className={`p-3 rounded-lg ${stat.bgColor}`}>
                  <stat.icon className={`w-6 h-6 ${stat.color}`} />
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Real-Time Metrics */}
        {apiKey && (
          <div className="mb-8 bg-white p-6 rounded-lg border border-gray-200 shadow-sm">
            <RealTimeMetrics apiKey={apiKey} />
          </div>
        )}

        {/* Usage Trends */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          <div className="bg-white p-6 rounded-lg border border-gray-200 shadow-sm">
            <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <TrendingUp className="w-5 h-5 mr-2 text-blue-600" />
              Request Volume
            </h2>
            <UsageChart data={usageData} type="area" metric="requests" />
          </div>

          <div className="bg-white p-6 rounded-lg border border-gray-200 shadow-sm">
            <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <DollarSign className="w-5 h-5 mr-2 text-green-600" />
              Cost Trends
            </h2>
            <UsageChart data={usageData} type="line" metric="cost" />
          </div>
        </div>

        {/* Endpoint Breakdown */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          <div className="bg-white p-6 rounded-lg border border-gray-200 shadow-sm">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">
              Endpoint Distribution
            </h2>
            <EndpointBreakdown data={endpointData} />
          </div>

          <div className="bg-white p-6 rounded-lg border border-gray-200 shadow-sm">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">
              Cost by Service
            </h2>
            <CostBreakdown data={costData} height={400} />
          </div>
        </div>

        {/* Performance Metrics */}
        <div className="bg-white p-6 rounded-lg border border-gray-200 shadow-sm mb-8">
          <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <Activity className="w-5 h-5 mr-2 text-purple-600" />
            Performance Overview
          </h2>
          <PerformanceMetrics data={performanceData} height={350} />
        </div>

        {/* Loading State */}
        {loading && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white p-6 rounded-lg shadow-xl">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
              <p className="mt-4 text-gray-600">Loading analytics...</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
