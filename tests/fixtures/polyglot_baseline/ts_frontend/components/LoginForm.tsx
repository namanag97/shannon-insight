import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { useForm } from '../hooks/useForm';
import { validators } from '../utils/validators';
import { AuthPayload } from '../types/user';

export const LoginForm: React.FC = () => {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [apiError, setApiError] = useState<string | null>(null);

  const form = useForm<AuthPayload>({
    initialValues: {
      email: '',
      password: '',
    },
    validate: (values) => {
      const errors: Record<string, string> = {};

      const emailValidation = validators.email(values.email);
      if (!emailValidation.valid) {
        errors.email = emailValidation.error || 'Invalid email';
      }

      if (!values.password) {
        errors.password = 'Password is required';
      }

      return errors;
    },
    onSubmit: async (values) => {
      try {
        setApiError(null);
        await login(values);
        navigate('/dashboard');
      } catch (error) {
        const message = error instanceof Error ? error.message : 'Login failed';
        setApiError(message);
      }
    },
  });

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full bg-white rounded-lg shadow-md p-8">
        <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">Sign in to your account</h2>

        {apiError && (
          <div className="mt-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
            {apiError}
          </div>
        )}

        <form onSubmit={form.handleSubmit} className="mt-8 space-y-6">
          <div>
            <label htmlFor="email" className="block text-sm font-medium text-gray-700">
              Email address
            </label>
            <input
              id="email"
              type="email"
              {...form.getFieldProps('email')}
              className={`mt-1 block w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 ${
                form.getFieldError('email') ? 'border-red-500' : 'border-gray-300'
              }`}
              placeholder="user@example.com"
            />
            {form.getFieldError('email') && (
              <p className="mt-1 text-sm text-red-600">{form.getFieldError('email')}</p>
            )}
          </div>

          <div>
            <label htmlFor="password" className="block text-sm font-medium text-gray-700">
              Password
            </label>
            <input
              id="password"
              type="password"
              {...form.getFieldProps('password')}
              className={`mt-1 block w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 ${
                form.getFieldError('password') ? 'border-red-500' : 'border-gray-300'
              }`}
              placeholder="••••••••"
            />
            {form.getFieldError('password') && (
              <p className="mt-1 text-sm text-red-600">{form.getFieldError('password')}</p>
            )}
          </div>

          <button
            type="submit"
            disabled={form.isSubmitting}
            className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:bg-gray-400 font-medium"
          >
            {form.isSubmitting ? 'Signing in...' : 'Sign in'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default LoginForm;
