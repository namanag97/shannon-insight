import { Base } from "./base";

export interface Shape {
  area(): number;
}

export abstract class Shape2D extends Base {
  abstract area(): number;

  describe(): string {
    return this.name;
  }
}

export function make(): number {
  const f = (x: number): number => x * 2;
  return f(21);
}
