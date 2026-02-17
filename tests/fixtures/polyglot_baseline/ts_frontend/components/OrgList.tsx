import React, { useEffect, useState } from 'react';
import { usePaginatedApi } from '../hooks/useApi';
import { Organization } from '../types/organization';

interface OrgListProps {
  onEdit?: (org: Organization) => void;
  onDelete?: (orgId: string) => Promise<void>;
}

export const OrgList: React.FC<OrgListProps> = ({ onEdit, onDelete }) => {
  const { data, isLoading, error, fetch } = usePaginatedApi<Organization>();
  const [currentPage, setCurrentPage] = useState(1);
  const [deletingId, setDeletingId] = useState<string | null>(null);

  useEffect(() => {
    fetch('/organizations', currentPage, 10);
  }, [currentPage]);

  const handleDelete = async (orgId: string): Promise<void> => {
    if (!window.confirm('Are you sure you want to delete this organization?')) {
      return;
    }

    try {
      setDeletingId(orgId);
      await onDelete?.(orgId);
      fetch('/organizations', currentPage, 10);
    } finally {
      setDeletingId(null);
    }
  };

  if (isLoading) {
    return <div className="text-center py-8">Loading organizations...</div>;
  }

  if (error) {
    return (
      <div className="p-4 bg-red-100 border border-red-400 text-red-700 rounded">
        Error loading organizations: {error.message}
      </div>
    );
  }

  if (!data?.items.length) {
    return <div className="text-center py-8 text-gray-500">No organizations found.</div>;
  }

  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden">
      <table className="w-full">
        <thead className="bg-gray-100 border-b">
          <tr>
            <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Name</th>
            <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Slug</th>
            <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Plan</th>
            <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Members</th>
            <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Status</th>
            <th className="px-6 py-3 text-right text-sm font-semibold text-gray-700">Actions</th>
          </tr>
        </thead>
        <tbody>
          {data.items.map((org) => (
            <tr key={org.id} className="border-b hover:bg-gray-50">
              <td className="px-6 py-4 text-sm font-medium text-gray-900">{org.name}</td>
              <td className="px-6 py-4 text-sm text-gray-600">{org.slug}</td>
              <td className="px-6 py-4 text-sm">
                <span className="inline-block px-3 py-1 bg-purple-100 text-purple-800 rounded-full text-xs font-medium">
                  {org.plan.charAt(0).toUpperCase() + org.plan.slice(1)}
                </span>
              </td>
              <td className="px-6 py-4 text-sm text-gray-600">{org.memberCount}</td>
              <td className="px-6 py-4 text-sm">
                <span className={`inline-block px-3 py-1 rounded-full text-xs font-medium ${
                  org.isActive
                    ? 'bg-green-100 text-green-800'
                    : 'bg-gray-100 text-gray-800'
                }`}>
                  {org.isActive ? 'Active' : 'Inactive'}
                </span>
              </td>
              <td className="px-6 py-4 text-sm text-right space-x-2">
                <button
                  onClick={() => onEdit?.(org)}
                  className="text-blue-600 hover:text-blue-800 font-medium"
                >
                  Edit
                </button>
                <button
                  onClick={() => handleDelete(org.id)}
                  disabled={deletingId === org.id}
                  className="text-red-600 hover:text-red-800 font-medium disabled:text-gray-400"
                >
                  {deletingId === org.id ? 'Deleting...' : 'Delete'}
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {data.pages > 1 && (
        <div className="px-6 py-4 flex items-center justify-between border-t">
          <div className="text-sm text-gray-600">
            Page {data.page} of {data.pages}
          </div>
          <div className="space-x-2">
            <button
              onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
              disabled={currentPage === 1}
              className="px-3 py-1 bg-gray-200 text-gray-700 rounded disabled:bg-gray-100 disabled:text-gray-400"
            >
              Previous
            </button>
            <button
              onClick={() => setCurrentPage(Math.min(data.pages, currentPage + 1))}
              disabled={currentPage === data.pages}
              className="px-3 py-1 bg-gray-200 text-gray-700 rounded disabled:bg-gray-100 disabled:text-gray-400"
            >
              Next
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default OrgList;
