export interface Organization {
  id: string;
  name: string;
  slug: string;
  description?: string;
  logo?: string;
  website?: string;
  createdAt: string;
  updatedAt: string;
  memberCount: number;
  isActive: boolean;
  plan: 'free' | 'pro' | 'enterprise';
  billingEmail?: string;
}

export interface CreateOrgRequest {
  name: string;
  slug: string;
  description?: string;
  website?: string;
  billingEmail?: string;
}

export interface UpdateOrgRequest {
  name?: string;
  description?: string;
  website?: string;
  logo?: string;
  plan?: Organization['plan'];
}

export interface OrganizationMember {
  userId: string;
  userName: string;
  email: string;
  role: 'owner' | 'admin' | 'member';
  joinedAt: string;
}

export interface OrganizationStats {
  totalMembers: number;
  totalProjects: number;
  lastActivityAt: string;
}
