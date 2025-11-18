'use client';

import React, { useState, useEffect } from 'react';
import { Users, Building2, Plus, ChevronDown } from 'lucide-react';

interface Organization {
  id: string;
  name: string;
  slug: string;
  owner_id: string;
  member_count: number;
  is_active: boolean;
}

interface OrganizationSelectorProps {
  apiKey: string;
  onOrganizationChange?: (orgId: string | null) => void;
}

export default function OrganizationSelector({
  apiKey,
  onOrganizationChange,
}: OrganizationSelectorProps) {
  const [organizations, setOrganizations] = useState<Organization[]>([]);
  const [selectedOrg, setSelectedOrg] = useState<Organization | null>(null);
  const [isOpen, setIsOpen] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchOrganizations();
  }, [apiKey]);

  const fetchOrganizations = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/v1/teams/organizations', {
        headers: {
          'X-API-Key': apiKey,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setOrganizations(data);

        // Select first org by default
        if (data.length > 0 && !selectedOrg) {
          setSelectedOrg(data[0]);
          onOrganizationChange?.(data[0].id);
        }
      }
    } catch (error) {
      console.error('Failed to fetch organizations:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectOrg = (org: Organization) => {
    setSelectedOrg(org);
    setIsOpen(false);
    onOrganizationChange?.(org.id);
  };

  const handlePersonalMode = () => {
    setSelectedOrg(null);
    setIsOpen(false);
    onOrganizationChange?.(null);
  };

  if (loading) {
    return (
      <div className="animate-pulse bg-gray-200 h-10 rounded-lg w-48"></div>
    );
  }

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center space-x-2 px-4 py-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
      >
        {selectedOrg ? (
          <Building2 className="w-5 h-5 text-blue-600" />
        ) : (
          <Users className="w-5 h-5 text-gray-600" />
        )}
        <span className="font-medium text-gray-900">
          {selectedOrg ? selectedOrg.name : 'Personal'}
        </span>
        <ChevronDown className="w-4 h-4 text-gray-500" />
      </button>

      {isOpen && (
        <div className="absolute top-full mt-2 w-64 bg-white border border-gray-200 rounded-lg shadow-lg z-10">
          {/* Personal Mode */}
          <button
            onClick={handlePersonalMode}
            className={`w-full flex items-center space-x-3 px-4 py-3 hover:bg-gray-50 transition-colors border-b border-gray-200 ${
              !selectedOrg ? 'bg-blue-50' : ''
            }`}
          >
            <Users className="w-5 h-5 text-gray-600" />
            <div className="text-left">
              <div className="font-medium text-gray-900">Personal</div>
              <div className="text-xs text-gray-500">Your personal workspace</div>
            </div>
          </button>

          {/* Organizations */}
          {organizations.length > 0 && (
            <div className="py-1">
              <div className="px-4 py-2 text-xs font-semibold text-gray-500 uppercase">
                Organizations
              </div>
              {organizations.map((org) => (
                <button
                  key={org.id}
                  onClick={() => handleSelectOrg(org)}
                  className={`w-full flex items-center justify-between px-4 py-3 hover:bg-gray-50 transition-colors ${
                    selectedOrg?.id === org.id ? 'bg-blue-50' : ''
                  }`}
                >
                  <div className="flex items-center space-x-3">
                    <Building2 className="w-5 h-5 text-blue-600" />
                    <div className="text-left">
                      <div className="font-medium text-gray-900">{org.name}</div>
                      <div className="text-xs text-gray-500">
                        {org.member_count} {org.member_count === 1 ? 'member' : 'members'}
                      </div>
                    </div>
                  </div>
                </button>
              ))}
            </div>
          )}

          {/* Create Organization */}
          <button
            onClick={() => {
              setIsOpen(false);
              // Navigate to create organization page
              window.location.href = '/teams/create';
            }}
            className="w-full flex items-center space-x-3 px-4 py-3 hover:bg-gray-50 transition-colors border-t border-gray-200 text-blue-600"
          >
            <Plus className="w-5 h-5" />
            <span className="font-medium">Create Organization</span>
          </button>
        </div>
      )}

      {/* Backdrop */}
      {isOpen && (
        <div
          className="fixed inset-0 z-0"
          onClick={() => setIsOpen(false)}
        />
      )}
    </div>
  );
}
