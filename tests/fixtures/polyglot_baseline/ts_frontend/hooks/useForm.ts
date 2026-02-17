import { useState, useCallback, useMemo } from 'react';
import { validateForm } from '../utils/validators';

interface UseFormOptions<T> {
  initialValues: T;
  onSubmit: (values: T) => Promise<void> | void;
  validate?: (values: T) => Record<string, string>;
}

interface UseFormState<T> {
  values: T;
  errors: Record<string, string>;
  touched: Record<string, boolean>;
  isSubmitting: boolean;
  isDirty: boolean;
}

export const useForm = <T extends Record<string, unknown>>({
  initialValues,
  onSubmit,
  validate,
}: UseFormOptions<T>) => {
  const [state, setState] = useState<UseFormState<T>>({
    values: initialValues,
    errors: {},
    touched: {},
    isSubmitting: false,
    isDirty: false,
  });

  const handleChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
      const { name, value, type } = e.target;
      const fieldValue = type === 'checkbox' ? (e.target as HTMLInputElement).checked : value;

      setState((prev) => ({
        ...prev,
        values: { ...prev.values, [name]: fieldValue },
        isDirty: true,
      }));
    },
    []
  );

  const handleBlur = useCallback(
    (e: React.FocusEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
      const { name } = e.target;
      setState((prev) => ({
        ...prev,
        touched: { ...prev.touched, [name]: true },
      }));
    },
    []
  );

  const validateFields = useCallback((): boolean => {
    const errors = validate ? validate(state.values) : {};
    setState((prev) => ({
      ...prev,
      errors,
      touched: Object.keys(state.values).reduce((acc, key) => ({ ...acc, [key]: true }), {}),
    }));
    return Object.keys(errors).length === 0;
  }, [state.values, validate]);

  const handleSubmit = useCallback(
    async (e: React.FormEvent<HTMLFormElement>) => {
      e.preventDefault();

      if (!validateFields()) {
        return;
      }

      setState((prev) => ({ ...prev, isSubmitting: true }));

      try {
        await onSubmit(state.values);
        setState((prev) => ({
          ...prev,
          isSubmitting: false,
          isDirty: false,
        }));
      } catch (error) {
        console.error('Form submission error:', error);
        setState((prev) => ({
          ...prev,
          isSubmitting: false,
        }));
      }
    },
    [state.values, onSubmit, validateFields]
  );

  const setFieldValue = useCallback((name: string, value: unknown) => {
    setState((prev) => ({
      ...prev,
      values: { ...prev.values, [name]: value },
      isDirty: true,
    }));
  }, []);

  const setFieldError = useCallback((name: string, error: string) => {
    setState((prev) => ({
      ...prev,
      errors: { ...prev.errors, [name]: error },
    }));
  }, []);

  const reset = useCallback(() => {
    setState({
      values: initialValues,
      errors: {},
      touched: {},
      isSubmitting: false,
      isDirty: false,
    });
  }, [initialValues]);

  const getFieldProps = useCallback(
    (name: keyof T) => ({
      name: String(name),
      value: state.values[name],
      onChange: handleChange,
      onBlur: handleBlur,
    }),
    [state.values, handleChange, handleBlur]
  );

  const getFieldError = useCallback(
    (name: keyof T): string | undefined => {
      const key = String(name);
      return state.touched[key] ? state.errors[key] : undefined;
    },
    [state.errors, state.touched]
  );

  return useMemo(
    () => ({
      values: state.values,
      errors: state.errors,
      touched: state.touched,
      isSubmitting: state.isSubmitting,
      isDirty: state.isDirty,
      handleChange,
      handleBlur,
      handleSubmit,
      setFieldValue,
      setFieldError,
      reset,
      getFieldProps,
      getFieldError,
    }),
    [state, handleChange, handleBlur, handleSubmit, setFieldValue, setFieldError, reset, getFieldProps, getFieldError]
  );
};
