/**
 * Unit tests for helpers.
 */

import { describe, it, expect } from "vitest";
import { hColor, sevKey, polarColor } from "./helpers.js";

describe("hColor", () => {
  it("returns green for scores >= 8", () => {
    expect(hColor(8)).toBe("var(--green)");
    expect(hColor(10)).toBe("var(--green)");
  });

  it("returns yellow for scores 6-7.9", () => {
    expect(hColor(6)).toBe("var(--yellow)");
    expect(hColor(7.9)).toBe("var(--yellow)");
  });

  it("returns orange for scores 4-5.9", () => {
    expect(hColor(4)).toBe("var(--orange)");
    expect(hColor(5.9)).toBe("var(--orange)");
  });

  it("returns red for scores < 4", () => {
    expect(hColor(3.9)).toBe("var(--red)");
    expect(hColor(0)).toBe("var(--red)");
  });
});

describe("sevKey", () => {
  it("maps severity floats to keywords", () => {
    expect(sevKey(0.95)).toBe("critical");
    expect(sevKey(0.9)).toBe("critical");
    expect(sevKey(0.85)).toBe("high");
    expect(sevKey(0.8)).toBe("high");
    expect(sevKey(0.7)).toBe("medium");
    expect(sevKey(0.6)).toBe("medium");
    expect(sevKey(0.5)).toBe("low");
    expect(sevKey(0.4)).toBe("low");
    expect(sevKey(0.3)).toBe("info");
    expect(sevKey(0.0)).toBe("info");
  });
});

describe("polarColor", () => {
  it("returns red for high-is-bad signals with high values", () => {
    expect(polarColor("risk_score", 0.8)).toBe("var(--red)");
    expect(polarColor("churn_cv", 0.9)).toBe("var(--red)");
  });

  it("returns orange for moderate high-is-bad values", () => {
    expect(polarColor("risk_score", 0.3)).toBe("var(--orange)");
  });

  it("returns text for low high-is-bad values", () => {
    expect(polarColor("risk_score", 0.1)).toBe("var(--text)");
  });

  it("returns green for high-is-good signals with high values", () => {
    expect(polarColor("wiring_quality", 0.9)).toBe("var(--green)");
  });

  it("returns accent for neutral signals", () => {
    expect(polarColor("pagerank", 0.5)).toBe("var(--accent)");
    expect(polarColor("lines", 100)).toBe("var(--accent)");
  });

  it("handles unbounded signal normalization", () => {
    // cognitive_load cap = 25, so 12.5/25 = 0.5 -> orange
    expect(polarColor("cognitive_load", 12.5)).toBe("var(--orange)");
    // cognitive_load 15/25 = 0.6 -> red
    expect(polarColor("cognitive_load", 15)).toBe("var(--red)");
  });
});
