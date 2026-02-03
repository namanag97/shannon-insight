// Simple, clean TypeScript - low complexity
interface User {
  name: string;
  email: string;
  age?: number;
}

class UserService {
  private users: User[] = [];

  addUser(user: User): void {
    if (!this.isValidUser(user)) {
      throw new Error("Invalid user data");
    }
    this.users.push(user);
  }

  isValidUser(user: User): boolean {
    return !!user.name && !!user.email && user.email.includes("@");
  }

  getUsers(): User[] {
    return [...this.users];
  }

  findByEmail(email: string): User | undefined {
    return this.users.find((u) => u.email === email);
  }
}

export { UserService, User };
