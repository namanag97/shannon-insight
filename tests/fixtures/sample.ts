// Sample TypeScript file for testing tree-sitter parsing.

import { Something } from "./module";
import * as fs from "fs";

interface Greeter {
  greet(name: string): string;
}

abstract class BaseGreeter implements Greeter {
  abstract greet(name: string): string;
}

class HelloGreeter extends BaseGreeter {
  private prefix: string;

  constructor(prefix: string = "Hello") {
    super();
    this.prefix = prefix;
  }

  greet(name: string): string {
    return `${this.prefix}, ${name}!`;
  }

  private helper(): void {
    console.log("helper");
  }
}

function processData(data: number[]): number {
  let sum = 0;
  for (const v of data) {
    if (v > 0) {
      for (let i = 0; i < v; i++) {
        sum += i;
      }
    }
  }
  return sum;
}

const arrowFunc = (x: number): number => x * 2;

export { HelloGreeter, processData };
