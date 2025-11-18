'use client';

import React, { useState, useEffect } from 'react';
import {
  Users,
  UserPlus,
  Shield,
  Mail,
  Calendar,
  MoreVertical,
  Trash2,
  Edit,
} from 'lucide-react';

interface Member {
  id: string;
  user_id: string;
  organization_id: string;
  role: 'owner' | 'admin' | 'developer' | 'viewer';
  is_active: boolean;
  joined_at: string;
  user_email?: string;
  user_name?: string;
}

interface Organization {
  id: string;
  name: string;
  slug: string;
  owner_id: string;
  billing_email?: string;
  member_count: number;
}

export default function TeamsPage() {
  const [apiKey, setApiKey] = useState<string>('');
  const [organizations, setOrganizations] = useState<Organization[]>([]);
  const [selectedOrg, setSelectedOrg] = useState<Organization | null>(null);
  const [members, setMembers] = useState<Member[]>([]);
  const [loading, setLoading] = useState(true);
  const [showInviteModal, setShowInviteModal] = useState(false);
  const [inviteEmail, setInviteEmail] = useState('');
  const [inviteRole, setInviteRole] = useState<Member['role']>('developer');

  useEffect(() => {
    const key = localStorage.getItem('api_key');
    if (key) {
      setApiKey(key);
      fetchOrganizations(key);
    }
  }, []);

  useEffect(() => {
    if (selectedOrg && apiKey) {
      fetchMembers();
    }
  }, [selectedOrg, apiKey]);

  const fetchOrganizations = async (key: string) => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/v1/teams/organizations', {
        headers: {
          'X-API-Key': key,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setOrganizations(data);
        if (data.length > 0) {
          setSelectedOrg(data[0]);
        }
      }
    } catch (error) {
      console.error('Failed to fetch organizations:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchMembers = async () => {
    if (!selectedOrg) return;

    try {
      const response = await fetch(
        `http://localhost:8000/api/v1/teams/organizations/${selectedOrg.id}/members`,
        {
          headers: {
            'X-API-Key': apiKey,
          },
        }
      );

      if (response.ok) {
        const data = await response.json();
        setMembers(data);
      }
    } catch (error) {
      console.error('Failed to fetch members:', error);
    }
  };

  const handleInviteMember = async () => {
    if (!selectedOrg || !inviteEmail) return;

    try {
      const response = await fetch(
        `http://localhost:8000/api/v1/teams/organizations/${selectedOrg.id}/members`,
        {
          method: 'POST',
          headers: {
            'X-API-Key': apiKey,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            email: inviteEmail,
            role: inviteRole,
          }),
        }
      );

      if (response.ok) {
        setShowInviteModal(false);
        setInviteEmail('');
        setInviteRole('developer');
        fetchMembers();
      } else {
        const error = await response.json();
        alert(error.detail || 'Failed to invite member');
      }
    } catch (error) {
      console.error('Failed to invite member:', error);
      alert('Failed to invite member');
    }
  };

  const handleRemoveMember = async (memberId: string) => {
    if (!selectedOrg) return;
    if (!confirm('Are you sure you want to remove this member?')) return;

    try {
      const response = await fetch(
        `http://localhost:8000/api/v1/teams/organizations/${selectedOrg.id}/members/${memberId}`,
        {
          method: 'DELETE',
          headers: {
            'X-API-Key': apiKey,
          },
        }
      );

      if (response.ok) {
        fetchMembers();
      }
    } catch (error) {
      console.error('Failed to remove member:', error);
    }
  };

  const getRoleBadgeColor = (role: Member['role']) => {
    switch (role) {
      case 'owner':
        return 'bg-purple-100 text-purple-800';
      case 'admin':
        return 'bg-blue-100 text-blue-800';
      case 'developer':
        return 'bg-green-100 text-green-800';
      case 'viewer':
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 flex items-center">
            <Users className="w-8 h-8 mr-3 text-blue-600" />
            Team Management
          </h1>
          <p className="mt-2 text-gray-600">
            Manage your organization members and their permissions
          </p>
        </div>

        {/* Organization Selector */}
        {organizations.length > 0 && (
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Organization
            </label>
            <select
              value={selectedOrg?.id || ''}
              onChange={(e) => {
                const org = organizations.find((o) => o.id === e.target.value);
                setSelectedOrg(org || null);
              }}
              className="w-full max-w-md px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              {organizations.map((org) => (
                <option key={org.id} value={org.id}>
                  {org.name} ({org.member_count} members)
                </option>
              ))}
            </select>
          </div>
        )}

        {selectedOrg ? (
          <div className="bg-white rounded-lg border border-gray-200 shadow-sm">
            {/* Organization Info */}
            <div className="p-6 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-xl font-semibold text-gray-900">
                    {selectedOrg.name}
                  </h2>
                  <p className="text-sm text-gray-600 mt-1">
                    Slug: {selectedOrg.slug}
                  </p>
                  {selectedOrg.billing_email && (
                    <p className="text-sm text-gray-600 mt-1">
                      Billing: {selectedOrg.billing_email}
                    </p>
                  )}
                </div>
                <button
                  onClick={() => setShowInviteModal(true)}
                  className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  <UserPlus className="w-5 h-5" />
                  <span>Invite Member</span>
                </button>
              </div>
            </div>

            {/* Members List */}
            <div className="divide-y divide-gray-200">
              {members.map((member) => (
                <div
                  key={member.id}
                  className="p-6 hover:bg-gray-50 transition-colors"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-4">
                      <div className="w-12 h-12 rounded-full bg-blue-100 flex items-center justify-center">
                        <span className="text-lg font-semibold text-blue-600">
                          {member.user_email?.charAt(0).toUpperCase() || 'U'}
                        </span>
                      </div>
                      <div>
                        <div className="flex items-center space-x-2">
                          <h3 className="font-semibold text-gray-900">
                            {member.user_name || member.user_email}
                          </h3>
                          <span
                            className={`px-2 py-1 text-xs font-medium rounded-full ${getRoleBadgeColor(
                              member.role
                            )}`}
                          >
                            {member.role}
                          </span>
                        </div>
                        <div className="flex items-center space-x-4 mt-1 text-sm text-gray-600">
                          <div className="flex items-center space-x-1">
                            <Mail className="w-4 h-4" />
                            <span>{member.user_email}</span>
                          </div>
                          <div className="flex items-center space-x-1">
                            <Calendar className="w-4 h-4" />
                            <span>
                              Joined {new Date(member.joined_at).toLocaleDateString()}
                            </span>
                          </div>
                        </div>
                      </div>
                    </div>

                    {member.role !== 'owner' && (
                      <button
                        onClick={() => handleRemoveMember(member.id)}
                        className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                      >
                        <Trash2 className="w-5 h-5" />
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        ) : (
          <div className="bg-white rounded-lg border border-gray-200 shadow-sm p-12 text-center">
            <Users className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              No Organizations
            </h3>
            <p className="text-gray-600 mb-4">
              Create an organization to start collaborating with your team
            </p>
            <button
              onClick={() => (window.location.href = '/teams/create')}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Create Organization
            </button>
          </div>
        )}

        {/* Invite Modal */}
        {showInviteModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-6 w-full max-w-md">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">
                Invite Team Member
              </h2>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Email Address
                  </label>
                  <input
                    type="email"
                    value={inviteEmail}
                    onChange={(e) => setInviteEmail(e.target.value)}
                    placeholder="team@example.com"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Role
                  </label>
                  <select
                    value={inviteRole}
                    onChange={(e) =>
                      setInviteRole(e.target.value as Member['role'])
                    }
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="developer">Developer</option>
                    <option value="admin">Admin</option>
                    <option value="viewer">Viewer</option>
                  </select>
                </div>
              </div>

              <div className="flex space-x-3 mt-6">
                <button
                  onClick={() => setShowInviteModal(false)}
                  className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={handleInviteMember}
                  className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  Send Invite
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
