import React, { useState } from 'react';
import { OrgList } from '../components/OrgList';
import { OrgForm } from '../components/OrgForm';
import { useApi } from '../hooks/useApi';
import { Organization } from '../types/organization';

export const OrganizationsPage: React.FC = () => {
  const [selectedOrg, setSelectedOrg] = useState<Organization | undefined>();
  const [showForm, setShowForm] = useState(false);
  const { remove } = useApi();

  const handleEdit = (org: Organization): void => {
    setSelectedOrg(org);
    setShowForm(true);
  };

  const handleCreate = (): void => {
    setSelectedOrg(undefined);
    setShowForm(true);
  };

  const handleCloseForm = (): void => {
    setShowForm(false);
    setSelectedOrg(undefined);
  };

  const handleDelete = async (orgId: string): Promise<void> => {
    try {
      await remove(`/organizations/${orgId}`);
    } catch (error) {
      console.error('Failed to delete organization:', error);
      throw error;
    }
  };

  const handleSuccess = (): void => {
    handleCloseForm();
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900">Organizations</h1>
        <button
          onClick={handleCreate}
          className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 font-medium"
        >
          Add Organization
        </button>
      </div>

      {showForm ? (
        <OrgForm
          organization={selectedOrg}
          onSuccess={handleSuccess}
          onCancel={handleCloseForm}
        />
      ) : (
        <OrgList onEdit={handleEdit} onDelete={handleDelete} />
      )}
    </div>
  );
};

export default OrganizationsPage;
