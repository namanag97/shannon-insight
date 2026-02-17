import axios, { AxiosInstance, AxiosError, AxiosResponse } from 'axios';
import { storage } from './storage';
import { ApiError, ApiResponse } from '../types/api';

const createApiClient = (): AxiosInstance => {
  const client = axios.create({
    baseURL: process.env.REACT_APP_API_URL || 'http://localhost:3001/api',
    timeout: 30000,
    headers: {
      'Content-Type': 'application/json',
    },
  });

  client.interceptors.request.use(
    (config) => {
      const token = storage.getAccessToken();
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    },
    (error) => Promise.reject(error)
  );

  client.interceptors.response.use(
    (response) => response,
    async (error: AxiosError) => {
      const originalRequest = error.config as any;

      if (error.response?.status === 401 && !originalRequest._retry) {
        originalRequest._retry = true;

        try {
          const refreshToken = storage.getRefreshToken();
          if (!refreshToken) {
            throw new Error('No refresh token available');
          }

          const response = await axios.post(
            `${process.env.REACT_APP_API_URL || 'http://localhost:3001/api'}/auth/refresh`,
            { refreshToken }
          );

          const { accessToken } = response.data;
          storage.setAccessToken(accessToken);

          originalRequest.headers.Authorization = `Bearer ${accessToken}`;
          return client(originalRequest);
        } catch (refreshError) {
          storage.clear();
          window.location.href = '/login';
          return Promise.reject(refreshError);
        }
      }

      return Promise.reject(error);
    }
  );

  return client;
};

export const apiClient = createApiClient();

export const handleApiError = (error: unknown): ApiError => {
  if (axios.isAxiosError(error)) {
    const apiError = new Error(
      error.response?.data?.error || error.message || 'An error occurred'
    ) as ApiError;
    apiError.status = error.response?.status;
    apiError.code = error.code;
    apiError.details = error.response?.data?.details;
    return apiError;
  }
  return error as ApiError;
};

export const get = async <T>(url: string): Promise<ApiResponse<T>> => {
  try {
    const response: AxiosResponse<ApiResponse<T>> = await apiClient.get(url);
    return response.data;
  } catch (error) {
    throw handleApiError(error);
  }
};

export const post = async <T>(url: string, data?: unknown): Promise<ApiResponse<T>> => {
  try {
    const response: AxiosResponse<ApiResponse<T>> = await apiClient.post(url, data);
    return response.data;
  } catch (error) {
    throw handleApiError(error);
  }
};

export const put = async <T>(url: string, data?: unknown): Promise<ApiResponse<T>> => {
  try {
    const response: AxiosResponse<ApiResponse<T>> = await apiClient.put(url, data);
    return response.data;
  } catch (error) {
    throw handleApiError(error);
  }
};

export const del = async <T>(url: string): Promise<ApiResponse<T>> => {
  try {
    const response: AxiosResponse<ApiResponse<T>> = await apiClient.delete(url);
    return response.data;
  } catch (error) {
    throw handleApiError(error);
  }
};
