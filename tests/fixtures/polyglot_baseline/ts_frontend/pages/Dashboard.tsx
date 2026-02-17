import React from 'react';
import { useAuth } from '../hooks/useAuth';

export const Dashboard: React.FC = () => {
  const { user } = useAuth();

  return (
    <div className="space-y-8">
      <div className="bg-white rounded-lg shadow-md p-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Welcome, {user?.name}!</h1>
        <p className="text-gray-600">You are logged in as {user?.email}</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Users</h3>
          <p className="text-4xl font-bold text-blue-600">--</p>
          <p className="text-sm text-gray-600 mt-2">Manage team members</p>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Organizations</h3>
          <p className="text-4xl font-bold text-purple-600">--</p>
          <p className="text-sm text-gray-600 mt-2">Manage organizations</p>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Role</h3>
          <p className="text-2xl font-bold text-green-600 capitalize">{user?.role}</p>
          <p className="text-sm text-gray-600 mt-2">Your account role</p>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">Account Information</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="text-sm font-medium text-gray-600">Email</label>
            <p className="text-lg text-gray-900">{user?.email}</p>
          </div>
          <div>
            <label className="text-sm font-medium text-gray-600">Name</label>
            <p className="text-lg text-gray-900">{user?.name}</p>
          </div>
          <div>
            <label className="text-sm font-medium text-gray-600">Organization ID</label>
            <p className="text-lg text-gray-900">{user?.organizationId}</p>
          </div>
          <div>
            <label className="text-sm font-medium text-gray-600">Member Since</label>
            <p className="text-lg text-gray-900">{new Date(user?.createdAt || '').toLocaleDateString()}</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
