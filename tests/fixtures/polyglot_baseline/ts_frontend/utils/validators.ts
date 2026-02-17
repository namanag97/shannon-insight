export const validators = {
  email: (email: string): { valid: boolean; error?: string } => {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!email) {
      return { valid: false, error: 'Email is required' };
    }
    if (!re.test(email)) {
      return { valid: false, error: 'Invalid email format' };
    }
    return { valid: true };
  },

  password: (password: string): { valid: boolean; error?: string } => {
    if (!password) {
      return { valid: false, error: 'Password is required' };
    }
    if (password.length < 8) {
      return { valid: false, error: 'Password must be at least 8 characters' };
    }
    if (!/[A-Z]/.test(password)) {
      return { valid: false, error: 'Password must contain uppercase letter' };
    }
    if (!/[0-9]/.test(password)) {
      return { valid: false, error: 'Password must contain number' };
    }
    return { valid: true };
  },

  name: (name: string): { valid: boolean; error?: string } => {
    if (!name || name.trim().length === 0) {
      return { valid: false, error: 'Name is required' };
    }
    if (name.length > 100) {
      return { valid: false, error: 'Name must be 100 characters or less' };
    }
    return { valid: true };
  },

  slug: (slug: string): { valid: boolean; error?: string } => {
    const re = /^[a-z0-9-]+$/;
    if (!slug) {
      return { valid: false, error: 'Slug is required' };
    }
    if (!re.test(slug)) {
      return { valid: false, error: 'Slug must contain only lowercase letters, numbers, and hyphens' };
    }
    if (slug.startsWith('-') || slug.endsWith('-')) {
      return { valid: false, error: 'Slug cannot start or end with hyphen' };
    }
    return { valid: true };
  },

  url: (url: string): { valid: boolean; error?: string } => {
    try {
      new URL(url);
      return { valid: true };
    } catch {
      return { valid: false, error: 'Invalid URL format' };
    }
  },
};

export const validateForm = (
  data: Record<string, unknown>,
  schema: Record<string, (value: unknown) => { valid: boolean; error?: string }>
): Record<string, string> => {
  const errors: Record<string, string> = {};

  Object.entries(schema).forEach(([key, validator]) => {
    const result = validator(data[key]);
    if (!result.valid && result.error) {
      errors[key] = result.error;
    }
  });

  return errors;
};
