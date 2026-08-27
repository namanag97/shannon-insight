import { helper } from "./util";
const fs = require("fs");

export function top(a) {
  if (a) {
    return 1;
  }
  return 0;
}

export class Widget {
  render(x) {
    return x ? this : null;
  }
}

const arrow = (n) => n + 1;
