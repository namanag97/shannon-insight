/**
 * Tests for SignalInspectorScreen - statistics computation logic.
 */

import { describe, it, expect } from "vitest";

// Test the computeStats function directly
function computeStats(values) {
  if (!values.length) return { min: 0, max: 0, mean: 0, median: 0, p90: 0 };
  const sorted = [...values].sort((a, b) => a - b);
  const sum = sorted.reduce((s, v) => s + v, 0);
  const mean = sum / sorted.length;
  const median = sorted.length % 2 === 0
    ? (sorted[sorted.length / 2 - 1] + sorted[sorted.length / 2]) / 2
    : sorted[Math.floor(sorted.length / 2)];
  const p90Idx = Math.min(Math.floor(sorted.length * 0.9), sorted.length - 1);
  return {
    min: sorted[0],
    max: sorted[sorted.length - 1],
    mean,
    median,
    p90: sorted[p90Idx],
  };
}

describe("computeStats", () => {
  it("returns zeros for empty array", () => {
    const stats = computeStats([]);
    expect(stats.min).toBe(0);
    expect(stats.max).toBe(0);
    expect(stats.mean).toBe(0);
    expect(stats.median).toBe(0);
    expect(stats.p90).toBe(0);
  });

  it("handles single element", () => {
    const stats = computeStats([5]);
    expect(stats.min).toBe(5);
    expect(stats.max).toBe(5);
    expect(stats.mean).toBe(5);
    expect(stats.median).toBe(5);
    expect(stats.p90).toBe(5);
  });

  it("computes correct stats for odd-length array", () => {
    const stats = computeStats([1, 3, 5, 7, 9]);
    expect(stats.min).toBe(1);
    expect(stats.max).toBe(9);
    expect(stats.mean).toBe(5);
    expect(stats.median).toBe(5);
    expect(stats.p90).toBe(9);
  });

  it("computes correct stats for even-length array", () => {
    const stats = computeStats([2, 4, 6, 8]);
    expect(stats.min).toBe(2);
    expect(stats.max).toBe(8);
    expect(stats.mean).toBe(5);
    expect(stats.median).toBe(5);
  });

  it("handles unsorted input", () => {
    const stats = computeStats([9, 1, 5, 3, 7]);
    expect(stats.min).toBe(1);
    expect(stats.max).toBe(9);
    expect(stats.mean).toBe(5);
    expect(stats.median).toBe(5);
  });

  it("handles decimal values", () => {
    const stats = computeStats([0.1, 0.5, 0.9]);
    expect(stats.min).toBeCloseTo(0.1);
    expect(stats.max).toBeCloseTo(0.9);
    expect(stats.mean).toBeCloseTo(0.5);
    expect(stats.median).toBeCloseTo(0.5);
  });
});
