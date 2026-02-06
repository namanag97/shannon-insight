// Sample JavaScript file for testing tree-sitter parsing.

const fs = require("fs");
import { Something } from "./module";

class HelloGreeter {
  constructor(prefix = "Hello") {
    this.prefix = prefix;
  }

  greet(name) {
    return `${this.prefix}, ${name}!`;
  }

  #privateHelper() {
    console.log("helper");
  }
}

function processData(data) {
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

const arrowFunc = (x) => x * 2;

function* generatorFunc() {
  yield 1;
  yield 2;
}

module.exports = { HelloGreeter, processData };
