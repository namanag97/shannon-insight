/**
 * Unit tests for constants — verifies structural integrity.
 */

import { describe, it, expect } from "vitest";
import {
  SIGNAL_LABELS,
  SIGNAL_CATEGORIES,
  SIGNAL_POLARITY,
  CATEGORY_ORDER,
  CATEGORY_LABELS,
  SCREENS,
  SEVERITY_LEVELS,
} from "./constants.js";

describe("SIGNAL_LABELS", () => {
  it("maps all signal keys to human labels", () => {
    expect(typeof SIGNAL_LABELS).toBe("object");
    expect(Object.keys(SIGNAL_LABELS).length).toBeGreaterThan(20);
    expect(SIGNAL_LABELS.risk_score).toBe("Overall Risk Score");
    expect(SIGNAL_LABELS.lines).toBe("Lines of Code");
  });
});

describe("SIGNAL_CATEGORIES", () => {
  it("has correct structure", () => {
    expect(SIGNAL_CATEGORIES).toBeInstanceOf(Array);
    expect(SIGNAL_CATEGORIES.length).toBe(6);
    for (const cat of SIGNAL_CATEGORIES) {
      expect(cat).toHaveProperty("key");
      expect(cat).toHaveProperty("name");
      expect(cat).toHaveProperty("signals");
      expect(cat.signals).toBeInstanceOf(Array);
      expect(cat.signals.length).toBeGreaterThan(0);
    }
  });

  it("all categorized signals have labels", () => {
    for (const cat of SIGNAL_CATEGORIES) {
      for (const sig of cat.signals) {
        expect(SIGNAL_LABELS).toHaveProperty(sig);
      }
    }
  });
});

describe("SIGNAL_POLARITY", () => {
  it("has entries for known signals", () => {
    expect(SIGNAL_POLARITY.risk_score).toBe(true);
    expect(SIGNAL_POLARITY.wiring_quality).toBe(false);
    expect(SIGNAL_POLARITY.pagerank).toBe(null);
  });
});

describe("CATEGORY_ORDER", () => {
  it("has 4 categories", () => {
    expect(CATEGORY_ORDER).toEqual(["incomplete", "fragile", "tangled", "team"]);
  });

  it("all categories have labels", () => {
    for (const key of CATEGORY_ORDER) {
      expect(CATEGORY_LABELS).toHaveProperty(key);
    }
  });
});

describe("SCREENS", () => {
  it("has 8 screens in order", () => {
    expect(SCREENS).toEqual(["overview", "issues", "files", "modules", "health", "graph", "churn", "signals"]);
  });
});

describe("SEVERITY_LEVELS", () => {
  it("has all 5 levels", () => {
    expect(SEVERITY_LEVELS).toEqual(["critical", "high", "medium", "low", "info"]);
  });
});
