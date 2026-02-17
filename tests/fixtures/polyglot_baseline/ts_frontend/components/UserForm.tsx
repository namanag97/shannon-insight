import React, { useState, useEffect } from 'react';
import { useForm } from '../hooks/useForm';
import { useApi } from '../hooks/useApi';
import { User, CreateUserRequest, UpdateUserRequest, UserRole } from '../types/user';
import { validators } from '../utils/validators';

interface UserFormProps {
  user?: User;
  onSuccess?: () => void;
  onCancel?: () => void;
}

const ROLES: UserRole[] = ['admin', 'manager', 'member', 'viewer'];

export const UserForm: React.FC<UserFormProps> = ({ user, onSuccess, onCancel }) => {
  const { create, update, error: apiError } = useApi();
  const [apiErrorMessage, setApiErrorMessage] = useState<string | null>(null);
  const isEditMode = !!user;

  const form = useForm<CreateUserRequest>({
    initialValues: {
      email: user?.email || '',
      name: user?.name || '',
      role: user?.role || 'member',
      organizationId: user?.organizationId || '',
      password: '',
    },
    validate: (values) => {
      const errors: Record<string, string> = {};

      const nameValidation = validators.name(values.name);
      if (!nameValidation.valid) {
        errors.name = nameValidation.error || 'Invalid name';
      }

      const emailValidation = validators.email(values.email);
      if (!emailValidation.valid) {
        errors.email = emailValidation.error || 'Invalid email';
      }

      if (!isEditMode && !values.password) {
        errors.password = 'Password is required for new users';
      } else if (values.password && values.password.length > 0) {
        const passwordValidation = validators.password(values.password);
        if (!passwordValidation.valid) {
          errors.password = passwordValidation.error || 'Invalid password';
        }
      }

      if (!values.organizationId) {
        errors.organizationId = 'Organization is required';
      }

      return errors;
    },
    onSubmit: async (values) => {
      try {
        setApiErrorMessage(null);

        if (isEditMode && user) {
          const updateData: UpdateUserRequest = {
            name: values.name,
            email: values.email,
            role: values.role,
          };
          await update(`/users/${user.id}`, updateData);
        } else {
          await create('/users', values);
        }

        onSuccess?.();
      } catch (error) {
        const message = error instanceof Error ? error.message : 'An error occurred';
        setApiErrorMessage(message);
      }
    },
  });

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-2xl font-bold mb-4">{isEditMode ? 'Edit User' : 'Create User'}</h2>

      {(apiError || apiErrorMessage) && (
        <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
          {apiErrorMessage || apiError?.message}
        </div>
      )}

      <form onSubmit={form.handleSubmit} className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-1">
              Name
            </label>
            <input
              id="name"
              type="text"
              {...form.getFieldProps('name')}
              className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-blue-500 ${
                form.getFieldError('name') ? 'border-red-500' : 'border-gray-300'
              }`}
              placeholder="John Doe"
            />
            {form.getFieldError('name') && (
              <p className="mt-1 text-sm text-red-600">{form.getFieldError('name')}</p>
            )}
          </div>

          <div>
            <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
              Email
            </label>
            <input
              id="email"
              type="email"
              {...form.getFieldProps('email')}
              disabled={isEditMode}
              className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-blue-500 ${
                isEditMode ? 'bg-gray-100 cursor-not-allowed' : ''
              } ${form.getFieldError('email') ? 'border-red-500' : 'border-gray-300'}`}
              placeholder="john@example.com"
            />
            {form.getFieldError('email') && (
              <p className="mt-1 text-sm text-red-600">{form.getFieldError('email')}</p>
            )}
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label htmlFor="role" className="block text-sm font-medium text-gray-700 mb-1">
              Role
            </label>
            <select
              id="role"
              {...form.getFieldProps('role')}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500"
            >
              {ROLES.map((role) => (
                <option key={role} value={role}>
                  {role.charAt(0).toUpperCase() + role.slice(1)}
                </option>
              ))}
            </select>
          </div>

          {!isEditMode && (
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-1">
                Password
              </label>
              <input
                id="password"
                type="password"
                {...form.getFieldProps('password')}
                className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-blue-500 ${
                  form.getFieldError('password') ? 'border-red-500' : 'border-gray-300'
                }`}
                placeholder="••••••••"
              />
              {form.getFieldError('password') && (
                <p className="mt-1 text-sm text-red-600">{form.getFieldError('password')}</p>
              )}
            </div>
          )}
        </div>

        <div className="flex space-x-3 pt-4">
          <button
            type="submit"
            disabled={form.isSubmitting}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400"
          >
            {form.isSubmitting ? 'Saving...' : isEditMode ? 'Update' : 'Create'}
          </button>
          <button
            type="button"
            onClick={onCancel}
            className="px-4 py-2 bg-gray-300 text-gray-700 rounded-md hover:bg-gray-400"
          >
            Cancel
          </button>
        </div>
      </form>
    </div>
  );
};

export default UserForm;
