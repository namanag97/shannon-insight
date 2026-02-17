import React, { useEffect, useState } from 'react';
import { usePaginatedApi } from '../hooks/useApi';
import { User } from '../types/user';

interface UserListProps {
  onEdit?: (user: User) => void;
  onDelete?: (userId: string) => Promise<void>;
}

export const UserList: React.FC<UserListProps> = ({ onEdit, onDelete }) => {
  const { data, isLoading, error, fetch, goToPage } = usePaginatedApi<User>();
  const [currentPage, setCurrentPage] = useState(1);
  const [deletingId, setDeletingId] = useState<string | null>(null);

  useEffect(() => {
    fetch('/users', currentPage, 10);
  }, [currentPage]);

  const handleDelete = async (userId: string): Promise<void> => {
    if (!window.confirm('Are you sure you want to delete this user?')) {
      return;
    }

    try {
      setDeletingId(userId);
      await onDelete?.(userId);
      fetch('/users', currentPage, 10);
    } finally {
      setDeletingId(null);
    }
  };

  if (isLoading) {
    return <div className="text-center py-8">Loading users...</div>;
  }

  if (error) {
    return (
      <div className="p-4 bg-red-100 border border-red-400 text-red-700 rounded">
        Error loading users: {error.message}
      </div>
    );
  }

  if (!data?.items.length) {
    return <div className="text-center py-8 text-gray-500">No users found.</div>;
  }

  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden">
      <table className="w-full">
        <thead className="bg-gray-100 border-b">
          <tr>
            <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Name</th>
            <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Email</th>
            <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Role</th>
            <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Status</th>
            <th className="px-6 py-3 text-right text-sm font-semibold text-gray-700">Actions</th>
          </tr>
        </thead>
        <tbody>
          {data.items.map((user) => (
            <tr key={user.id} className="border-b hover:bg-gray-50">
              <td className="px-6 py-4 text-sm text-gray-900">{user.name}</td>
              <td className="px-6 py-4 text-sm text-gray-600">{user.email}</td>
              <td className="px-6 py-4 text-sm">
                <span className="inline-block px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-xs font-medium">
                  {user.role}
                </span>
              </td>
              <td className="px-6 py-4 text-sm">
                <span className={`inline-block px-3 py-1 rounded-full text-xs font-medium ${
                  user.isActive
                    ? 'bg-green-100 text-green-800'
                    : 'bg-gray-100 text-gray-800'
                }`}>
                  {user.isActive ? 'Active' : 'Inactive'}
                </span>
              </td>
              <td className="px-6 py-4 text-sm text-right space-x-2">
                <button
                  onClick={() => onEdit?.(user)}
                  className="text-blue-600 hover:text-blue-800 font-medium"
                >
                  Edit
                </button>
                <button
                  onClick={() => handleDelete(user.id)}
                  disabled={deletingId === user.id}
                  className="text-red-600 hover:text-red-800 font-medium disabled:text-gray-400"
                >
                  {deletingId === user.id ? 'Deleting...' : 'Delete'}
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
              onClick={() => {
                setCurrentPage(Math.max(1, currentPage - 1));
              }}
              disabled={currentPage === 1}
              className="px-3 py-1 bg-gray-200 text-gray-700 rounded disabled:bg-gray-100 disabled:text-gray-400"
            >
              Previous
            </button>
            <button
              onClick={() => {
                setCurrentPage(Math.min(data.pages, currentPage + 1));
              }}
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

export default UserList;
