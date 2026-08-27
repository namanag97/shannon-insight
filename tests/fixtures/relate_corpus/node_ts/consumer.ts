import { fmt } from "@lib/util";
import { conf } from "./config";
import { log } from "./logger";
import { half } from "./mathx";
import { pad } from "./padder";
import cli from "b";
import { zip } from "lodash";
import { pad10 } from "left-pad";

export function report(x: string): string {
  return fmt(log(x)) + String(half(pad(conf.debug ? 1 : 2))) + zip([1]) + pad10(cli());
}
