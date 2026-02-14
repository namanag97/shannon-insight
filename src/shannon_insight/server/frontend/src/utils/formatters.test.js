/**
 * Unit tests for formatters.
 */

import { describe, it, expect } from "vitest";
import { fmtN, fmtF, fmtSigVal } from "./formatters.js";

describe("fmtN", () => {
  it("returns -- for null/undefined", () => {
    expect(fmtN(null)).toBe("--");
    expect(fmtN(undefined)).toBe("--");
  });

  it("formats small numbers as-is", () => {
    expect(fmtN(42)).toBe("42");
    expect(fmtN(0)).toBe("0");
    expect(fmtN(999)).toBe("999");
  });

  it("formats thousands with k suffix", () => {
    expect(fmtN(1000)).toBe("1.0k");
    expect(fmtN(1500)).toBe("1.5k");
    expect(fmtN(12345)).toBe("12.3k");
  });
});

describe("fmtF", () => {
  it("returns -- for null/undefined", () => {
    expect(fmtF(null)).toBe("--");
    expect(fmtF(undefined)).toBe("--");
  });

  it("formats with default 2 decimals", () => {
    expect(fmtF(3.14159)).toBe("3.14");
  });

  it("respects custom decimal count", () => {
    expect(fmtF(3.14159, 4)).toBe("3.1416");
    expect(fmtF(3.14159, 0)).toBe("3");
    expect(fmtF(3.14159, 1)).toBe("3.1");
  });
});

describe("fmtSigVal", () => {
  it("returns -- for null/undefined", () => {
    expect(fmtSigVal("any", null)).toBe("--");
    expect(fmtSigVal("any", undefined)).toBe("--");
  });

  it("formats booleans", () => {
    expect(fmtSigVal("is_orphan", true)).toBe("Yes");
    expect(fmtSigVal("is_orphan", false)).toBe("No");
  });

  it("formats ratio signals as percentage", () => {
    expect(fmtSigVal("stub_ratio", 0.5)).toBe("50.0%");
    expect(fmtSigVal("fix_ratio", 0.123)).toBe("12.3%");
    expect(fmtSigVal("compression_ratio", 1.0)).toBe("100.0%");
    expect(fmtSigVal("semantic_coherence", 0.0)).toBe("0.0%");
  });

  it("formats score signals to 3 decimals", () => {
    expect(fmtSigVal("risk_score", 0.123456)).toBe("0.123");
    expect(fmtSigVal("raw_risk", 0.5)).toBe("0.500");
    expect(fmtSigVal("wiring_quality", 0.999)).toBe("0.999");
  });

  it("formats precision signals to 4 decimals", () => {
    expect(fmtSigVal("pagerank", 0.001234)).toBe("0.0012");
    expect(fmtSigVal("betweenness", 0.5)).toBe("0.5000");
    expect(fmtSigVal("churn_cv", 1.234567)).toBe("1.2346");
  });

  it("formats integers as-is", () => {
    expect(fmtSigVal("lines", 42)).toBe("42");
    expect(fmtSigVal("total_changes", 100)).toBe("100");
  });

  it("formats other floats to 2 decimals", () => {
    expect(fmtSigVal("unknown_signal", 1.2345)).toBe("1.23");
  });

  it("formats strings as-is", () => {
    expect(fmtSigVal("role", "MODEL")).toBe("MODEL");
  });
});
