import { conf } from "./config";

export function half(n: number): number {
  return conf.debug ? n : n / 2;
}
