import React, { useState } from 'react';
import { useForm } from '../hooks/useForm';
import { useApi } from '../hooks/useApi';
import { Organization, CreateOrgRequest, UpdateOrgRequest } from '../types/organization';
import { validators } from '../utils/validators';

interface OrgFormProps {
  organization?: Organization;
  onSuccess?: () => void;
  onCancel?: () => void;
}

const PLANS: Array<'free' | 'pro' | 'enterprise'> = ['free', 'pro', 'enterprise'];

export const OrgForm: React.FC<OrgFormProps> = ({ organization, onSuccess, onCancel }) => {
  const { create, update, error: apiError } = useApi();
  const [apiErrorMessage, setApiErrorMessage] = useState<string | null>(null);
  const isEditMode = !!organization;

  const form = useForm<CreateOrgRequest>({
    initialValues: {
      name: organization?.name || '',
      slug: organization?.slug || '',
      description: organization?.description || '',
      website: organization?.website || '',
      billingEmail: organization?.billingEmail || '',
    },
    validate: (values) => {
      const errors: Record<string, string> = {};

      const nameValidation = validators.name(values.name);
      if (!nameValidation.valid) {
        errors.name = nameValidation.error || 'Invalid name';
      }

      const slugValidation = validators.slug(values.slug);
      if (!slugValidation.valid) {
        errors.slug = slugValidation.error || 'Invalid slug';
      }

      if (values.website) {
        const urlValidation = validators.url(values.website);
        if (!urlValidation.valid) {
          errors.website = urlValidation.error || 'Invalid URL';
        }
      }

      if (values.billingEmail) {
        const emailValidation = validators.email(values.billingEmail);
        if (!emailValidation.valid) {
          errors.billingEmail = emailValidation.error || 'Invalid email';
        }
      }

      return errors;
    },
    onSubmit: async (values) => {
      try {
        setApiErrorMessage(null);

        if (isEditMode && organization) {
          const updateData: UpdateOrgRequest = {
            name: values.name,
            description: values.description,
            website: values.website,
          };
          await update(`/organizations/${organization.id}`, updateData);
        } else {
          await create('/organizations', values);
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
      <h2 className="text-2xl font-bold mb-4">{isEditMode ? 'Edit Organization' : 'Create Organization'}</h2>

      {(apiError || apiErrorMessage) && (
        <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
          {apiErrorMessage || apiError?.message}
        </div>
      )}

      <form onSubmit={form.handleSubmit} className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-1">
              Organization Name
            </label>
            <input
              id="name"
              type="text"
              {...form.getFieldProps('name')}
              className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-blue-500 ${
                form.getFieldError('name') ? 'border-red-500' : 'border-gray-300'
              }`}
              placeholder="Acme Corp"
            />
            {form.getFieldError('name') && (
              <p className="mt-1 text-sm text-red-600">{form.getFieldError('name')}</p>
            )}
          </div>

          <div>
            <label htmlFor="slug" className="block text-sm font-medium text-gray-700 mb-1">
              Slug
            </label>
            <input
              id="slug"
              type="text"
              {...form.getFieldProps('slug')}
              disabled={isEditMode}
              className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-blue-500 ${
                isEditMode ? 'bg-gray-100 cursor-not-allowed' : ''
              } ${form.getFieldError('slug') ? 'border-red-500' : 'border-gray-300'}`}
              placeholder="acme-corp"
            />
            {form.getFieldError('slug') && (
              <p className="mt-1 text-sm text-red-600">{form.getFieldError('slug')}</p>
            )}
          </div>
        </div>

        <div>
          <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-1">
            Description
          </label>
          <textarea
            id="description"
            {...form.getFieldProps('description')}
            rows={3}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500"
            placeholder="Organization description..."
          />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label htmlFor="website" className="block text-sm font-medium text-gray-700 mb-1">
              Website
            </label>
            <input
              id="website"
              type="url"
              {...form.getFieldProps('website')}
              className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-blue-500 ${
                form.getFieldError('website') ? 'border-red-500' : 'border-gray-300'
              }`}
              placeholder="https://acme.com"
            />
            {form.getFieldError('website') && (
              <p className="mt-1 text-sm text-red-600">{form.getFieldError('website')}</p>
            )}
          </div>

          <div>
            <label htmlFor="billingEmail" className="block text-sm font-medium text-gray-700 mb-1">
              Billing Email
            </label>
            <input
              id="billingEmail"
              type="email"
              {...form.getFieldProps('billingEmail')}
              className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-blue-500 ${
                form.getFieldError('billingEmail') ? 'border-red-500' : 'border-gray-300'
              }`}
              placeholder="billing@acme.com"
            />
            {form.getFieldError('billingEmail') && (
              <p className="mt-1 text-sm text-red-600">{form.getFieldError('billingEmail')}</p>
            )}
          </div>
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

export default OrgForm;
