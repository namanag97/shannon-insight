import { conf } from "./config";

export function log(line: string): string {
  return conf.debug ? line : "";
}
