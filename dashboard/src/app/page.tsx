'use client';

import { useState, useEffect } from 'react';
import { APIKeysSection } from '@/components/APIKeysSection';
import { UsageStats } from '@/components/UsageStats';
import { CostAnalysis } from '@/components/CostAnalysis';
import { Header } from '@/components/Header';

export default function Dashboard() {
  const [apiKey, setApiKey] = useState<string>('');
  const [userData, setUserData] = useState<any>(null);

  useEffect(() => {
    // Load API key from localStorage
    const savedKey = localStorage.getItem('apiKey');
    if (savedKey) {
      setApiKey(savedKey);
      fetchUserData(savedKey);
    }
  }, []);

  const fetchUserData = async (key: string) => {
    try {
      const response = await fetch('/api/v1/manage/users/me', {
        headers: {
          'Authorization': `Bearer ${key}`,
        },
      });
      if (response.ok) {
        const data = await response.json();
        setUserData(data);
      }
    } catch (error) {
      console.error('Failed to fetch user data:', error);
    }
  };

  const handleApiKeySubmit = (key: string) => {
    localStorage.setItem('apiKey', key);
    setApiKey(key);
    fetchUserData(key);
  };

  if (!apiKey) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="max-w-md w-full bg-white shadow-lg rounded-lg p-8">
          <h1 className="text-2xl font-bold mb-4">Money API Dashboard</h1>
          <p className="text-gray-600 mb-6">
            Enter your API key to access the dashboard
          </p>
          <input
            type="password"
            placeholder="sk_..."
            className="w-full px-4 py-2 border rounded-lg mb-4"
            onKeyPress={(e) => {
              if (e.key === 'Enter') {
                handleApiKeySubmit((e.target as HTMLInputElement).value);
              }
            }}
          />
          <button
            onClick={(e) => {
              const input = e.currentTarget.previousElementSibling as HTMLInputElement;
              handleApiKeySubmit(input.value);
            }}
            className="w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700"
          >
            Login
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Header userData={userData} onLogout={() => {
        localStorage.removeItem('apiKey');
        setApiKey('');
        setUserData(null);
      }} />

      <main className="max-w-7xl mx-auto px-4 py-8 space-y-8">
        {/* Credit Balance */}
        {userData && (
          <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg p-6">
            <h2 className="text-lg font-semibold mb-2">Credit Balance</h2>
            <p className="text-4xl font-bold">${userData.credit_balance?.toFixed(2)}</p>
            <p className="text-sm mt-2 opacity-90">Plan: {userData.plan?.toUpperCase()}</p>
          </div>
        )}

        {/* API Keys */}
        <APIKeysSection apiKey={apiKey} />

        {/* Usage Statistics */}
        <UsageStats apiKey={apiKey} />

        {/* Cost Analysis */}
        <CostAnalysis apiKey={apiKey} />

        {/* Quick Links */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-bold mb-4">Quick Links</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <a
              href="/docs"
              className="p-4 border rounded-lg hover:border-blue-500 hover:shadow transition"
            >
              <h3 className="font-semibold mb-2">📚 Documentation</h3>
              <p className="text-sm text-gray-600">API reference and guides</p>
            </a>
            <a
              href="/redoc"
              className="p-4 border rounded-lg hover:border-blue-500 hover:shadow transition"
            >
              <h3 className="font-semibold mb-2">🔍 API Explorer</h3>
              <p className="text-sm text-gray-600">Interactive API testing</p>
            </a>
            <a
              href="https://github.com/yourusername/money-api-examples"
              className="p-4 border rounded-lg hover:border-blue-500 hover:shadow transition"
            >
              <h3 className="font-semibold mb-2">💻 Code Examples</h3>
              <p className="text-sm text-gray-600">Sample implementations</p>
            </a>
          </div>
        </div>
      </main>
    </div>
  );
}
