'use client';

import { useState, useEffect } from 'react';

interface APIKeySectionProps {
  apiKey: string;
}

export function APIKeysSection({ apiKey }: APIKeySectionProps) {
  const [keys, setKeys] = useState<any[]>([]);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [newKeyName, setNewKeyName] = useState('');
  const [createdKey, setCreatedKey] = useState<string | null>(null);

  useEffect(() => {
    fetchAPIKeys();
  }, [apiKey]);

  const fetchAPIKeys = async () => {
    try {
      const response = await fetch('/api/v1/manage/api-keys', {
        headers: { 'Authorization': `Bearer ${apiKey}` },
      });
      if (response.ok) {
        const data = await response.json();
        setKeys(data);
      }
    } catch (error) {
      console.error('Failed to fetch API keys:', error);
    }
  };

  const createAPIKey = async () => {
    try {
      const response = await fetch('/api/v1/manage/api-keys', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${apiKey}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ name: newKeyName }),
      });

      if (response.ok) {
        const data = await response.json();
        setCreatedKey(data.key);
        setNewKeyName('');
        setShowCreateForm(false);
        fetchAPIKeys();
      }
    } catch (error) {
      console.error('Failed to create API key:', error);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-xl font-bold">API Keys</h2>
        <button
          onClick={() => setShowCreateForm(true)}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          Create New Key
        </button>
      </div>

      {createdKey && (
        <div className="mb-4 p-4 bg-green-50 border border-green-200 rounded-lg">
          <p className="text-sm font-semibold text-green-800 mb-2">
            API Key Created! Save it now - you won't see it again.
          </p>
          <code className="block p-2 bg-white border rounded text-sm break-all">
            {createdKey}
          </code>
          <button
            onClick={() => {
              navigator.clipboard.writeText(createdKey);
              alert('Copied to clipboard!');
            }}
            className="mt-2 text-sm text-blue-600 hover:underline"
          >
            Copy to Clipboard
          </button>
        </div>
      )}

      {showCreateForm && (
        <div className="mb-4 p-4 border rounded-lg">
          <input
            type="text"
            placeholder="Key name (e.g., Production API)"
            value={newKeyName}
            onChange={(e) => setNewKeyName(e.target.value)}
            className="w-full px-4 py-2 border rounded-lg mb-2"
          />
          <div className="flex gap-2">
            <button
              onClick={createAPIKey}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              Create
            </button>
            <button
              onClick={() => {
                setShowCreateForm(false);
                setNewKeyName('');
              }}
              className="px-4 py-2 bg-gray-200 rounded-lg hover:bg-gray-300"
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      <div className="space-y-2">
        {keys.map((key) => (
          <div key={key.id} className="p-4 border rounded-lg flex justify-between items-center">
            <div>
              <p className="font-semibold">{key.name}</p>
              <p className="text-sm text-gray-600">
                {key.key_prefix}... • {key.rate_limit} RPM •
                {key.last_used ? ` Last used: ${new Date(key.last_used).toLocaleDateString()}` : ' Never used'}
              </p>
            </div>
            <div className="flex gap-2">
              <span className={`px-3 py-1 rounded text-sm ${key.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                {key.is_active ? 'Active' : 'Inactive'}
              </span>
            </div>
          </div>
        ))}
        {keys.length === 0 && (
          <p className="text-gray-500 text-center py-8">No API keys yet. Create one to get started!</p>
        )}
      </div>
    </div>
  );
}
