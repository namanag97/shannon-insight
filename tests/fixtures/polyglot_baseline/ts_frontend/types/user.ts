export interface User {
  id: string;
  email: string;
  name: string;
  role: UserRole;
  organizationId: string;
  createdAt: string;
  updatedAt: string;
  avatar?: string;
  isActive: boolean;
}

export type UserRole = 'admin' | 'manager' | 'member' | 'viewer';

export interface CreateUserRequest {
  email: string;
  name: string;
  role: UserRole;
  organizationId: string;
  password?: string;
}

export interface UpdateUserRequest {
  name?: string;
  email?: string;
  role?: UserRole;
  isActive?: boolean;
}

export interface AuthPayload {
  email: string;
  password: string;
}

export interface AuthResponse {
  user: User;
  accessToken: string;
  refreshToken: string;
  expiresIn: number;
}

export interface CurrentUser extends User {
  permissions?: string[];
}
