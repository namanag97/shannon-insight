import React, { useState } from 'react';
import { UserList } from '../components/UserList';
import { UserForm } from '../components/UserForm';
import { useApi } from '../hooks/useApi';
import { User } from '../types/user';

export const UsersPage: React.FC = () => {
  const [selectedUser, setSelectedUser] = useState<User | undefined>();
  const [showForm, setShowForm] = useState(false);
  const { remove } = useApi();

  const handleEdit = (user: User): void => {
    setSelectedUser(user);
    setShowForm(true);
  };

  const handleCreate = (): void => {
    setSelectedUser(undefined);
    setShowForm(true);
  };

  const handleCloseForm = (): void => {
    setShowForm(false);
    setSelectedUser(undefined);
  };

  const handleDelete = async (userId: string): Promise<void> => {
    try {
      await remove(`/users/${userId}`);
    } catch (error) {
      console.error('Failed to delete user:', error);
      throw error;
    }
  };

  const handleSuccess = (): void => {
    handleCloseForm();
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900">Users</h1>
        <button
          onClick={handleCreate}
          className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 font-medium"
        >
          Add User
        </button>
      </div>

      {showForm ? (
        <UserForm
          user={selectedUser}
          onSuccess={handleSuccess}
          onCancel={handleCloseForm}
        />
      ) : (
        <UserList onEdit={handleEdit} onDelete={handleDelete} />
      )}
    </div>
  );
};

export default UsersPage;
