import { useState, useCallback } from 'react';
import { ApiResponse, PaginatedResponse } from '../types/api';
import { get, post, put, del, handleApiError } from '../utils/api';

interface UseApiState<T> {
  data: T | null;
  error: Error | null;
  isLoading: boolean;
}

interface UseApiOptions {
  onSuccess?: (data: unknown) => void;
  onError?: (error: Error) => void;
}

export const useApi = <T,>(options?: UseApiOptions) => {
  const [state, setState] = useState<UseApiState<T>>({
    data: null,
    error: null,
    isLoading: false,
  });

  const request = useCallback(
    async (
      method: 'GET' | 'POST' | 'PUT' | 'DELETE',
      url: string,
      payload?: unknown
    ): Promise<T | null> => {
      setState({ data: null, error: null, isLoading: true });

      try {
        let response: ApiResponse<T>;

        switch (method) {
          case 'GET':
            response = await get<T>(url);
            break;
          case 'POST':
            response = await post<T>(url, payload);
            break;
          case 'PUT':
            response = await put<T>(url, payload);
            break;
          case 'DELETE':
            response = await del<T>(url);
            break;
        }

        const result = response.data || null;
        setState({ data: result, error: null, isLoading: false });
        options?.onSuccess?.(result);
        return result;
      } catch (error) {
        const apiError = handleApiError(error);
        setState({ data: null, error: apiError, isLoading: false });
        options?.onError?.(apiError);
        throw apiError;
      }
    },
    [options]
  );

  const fetch = useCallback(
    (url: string) => request('GET', url),
    [request]
  );

  const create = useCallback(
    (url: string, payload: unknown) => request('POST', url, payload),
    [request]
  );

  const update = useCallback(
    (url: string, payload: unknown) => request('PUT', url, payload),
    [request]
  );

  const remove = useCallback(
    (url: string) => request('DELETE', url),
    [request]
  );

  return {
    ...state,
    fetch,
    create,
    update,
    remove,
  };
};

export const usePaginatedApi = <T,>(options?: UseApiOptions) => {
  const [state, setState] = useState<UseApiState<PaginatedResponse<T>> & { page: number }>({
    data: null,
    error: null,
    isLoading: false,
    page: 1,
  });

  const fetch = useCallback(
    async (url: string, page: number = 1, limit: number = 20): Promise<PaginatedResponse<T> | null> => {
      setState((prev) => ({ ...prev, isLoading: true }));

      try {
        const response = await get<PaginatedResponse<T>>(`${url}?page=${page}&limit=${limit}`);
        const result = response.data || null;
        setState({ data: result, error: null, isLoading: false, page });
        options?.onSuccess?.(result);
        return result;
      } catch (error) {
        const apiError = handleApiError(error);
        setState((prev) => ({ ...prev, error: apiError, isLoading: false }));
        options?.onError?.(apiError);
        throw apiError;
      }
    },
    [options]
  );

  return {
    ...state,
    fetch,
    goToPage: (page: number, url: string, limit: number = 20) => fetch(url, page, limit),
  };
};
