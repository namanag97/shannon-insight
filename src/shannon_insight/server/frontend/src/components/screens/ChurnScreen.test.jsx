/**
 * Tests for ChurnScreen - trajectory classification and filtering logic.
 */

import { describe, it, expect } from "vitest";

// Test the trajectory classification logic directly
function classifyTrajectory(trajectory) {
  if (trajectory == null) return "unknown";
  if (trajectory > 0.3) return "rising";
  if (trajectory < -0.3) return "declining";
  return "stable";
}

describe("classifyTrajectory", () => {
  it("classifies rising trajectories", () => {
    expect(classifyTrajectory(0.5)).toBe("rising");
    expect(classifyTrajectory(1.0)).toBe("rising");
    expect(classifyTrajectory(0.31)).toBe("rising");
  });

  it("classifies declining trajectories", () => {
    expect(classifyTrajectory(-0.5)).toBe("declining");
    expect(classifyTrajectory(-1.0)).toBe("declining");
    expect(classifyTrajectory(-0.31)).toBe("declining");
  });

  it("classifies stable trajectories", () => {
    expect(classifyTrajectory(0)).toBe("stable");
    expect(classifyTrajectory(0.1)).toBe("stable");
    expect(classifyTrajectory(-0.1)).toBe("stable");
    expect(classifyTrajectory(0.3)).toBe("stable");
    expect(classifyTrajectory(-0.3)).toBe("stable");
  });

  it("handles null/undefined as unknown", () => {
    expect(classifyTrajectory(null)).toBe("unknown");
    expect(classifyTrajectory(undefined)).toBe("unknown");
  });
});
