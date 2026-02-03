// Medium complexity TypeScript - reasonable structure
import { User } from "./user_service";

type UserRole = "admin" | "user" | "guest";

interface Permission {
  resource: string;
  action: string;
}

class AuthService {
  private userRoles: Map<string, UserRole> = new Map();
  private rolePermissions: Map<UserRole, Permission[]> = new Map();

  constructor() {
    this.initializePermissions();
  }

  private initializePermissions(): void {
    this.rolePermissions.set("admin", [
      { resource: "*", action: "*" },
    ]);
    this.rolePermissions.set("user", [
      { resource: "posts", action: "read" },
      { resource: "posts", action: "create" },
    ]);
    this.rolePermissions.set("guest", [
      { resource: "posts", action: "read" },
    ]);
  }

  setUserRole(userId: string, role: UserRole): void {
    this.userRoles.set(userId, role);
  }

  getUserRole(userId: string): UserRole | undefined {
    return this.userRoles.get(userId);
  }

  hasPermission(userId: string, permission: Permission): boolean {
    const role = this.getUserRole(userId);
    if (!role) {
      return false;
    }

    const permissions = this.rolePermissions.get(role) || [];
    return permissions.some((p) => this.matchesPermission(p, permission));
  }

  private matchesPermission(required: Permission, granted: Permission): boolean {
    if (required.resource === "*" && granted.resource === "*") {
      return required.action === "*" || granted.action === "*";
    }

    return (
      (required.resource === "*" || required.resource === granted.resource) &&
      (required.action === "*" || required.action === granted.action)
    );
  }

  checkAccess(userId: string, resource: string, action: string): boolean {
    return this.hasPermission(userId, { resource, action });
  }
}

class UserManager {
  private authService: AuthService;

  constructor(authService: AuthService) {
    this.authService = authService;
  }

  createUser(user: User, role: UserRole = "guest"): void {
    const userId = this.generateUserId();
    this.authService.setUserRole(userId, role);
    console.log(`Created user ${userId} with role ${role}`);
  }

  updateUserRole(userId: string, role: UserRole): void {
    this.authService.setUserRole(userId, role);
  }

  canAccessResource(userId: string, resource: string, action: string): boolean {
    return this.authService.checkAccess(userId, resource, action);
  }

  private generateUserId(): string {
    return `user_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }
}

export { AuthService, UserManager, UserRole, Permission };
