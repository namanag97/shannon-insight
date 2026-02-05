#!/usr/bin/env python3
"""Experiment 03 — Dynamical Systems: Churn Trajectory Analysis.

Extracts per-file change counts over time, classifies trajectory shapes
(stabilizing, churning, spiking, dormant, burst-then-stable), and
renders ASCII sparklines.
"""

import subprocess
import sys
import time
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _bootstrap import load_analysis

SPARKLINE_CHARS = " ▁▂▃▄▅▆▇█"


def parse_git_log_with_time(codebase_path):
    """Parse git log to get (hash, timestamp, files) triples."""
    cmd = [
        "git", "-C", str(codebase_path),
        "log", "--format=%H %at", "--name-only",
    ]
    try:
        out = subprocess.check_output(cmd, text=True, stderr=subprocess.DEVNULL)
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []

    entries = []
    current_hash = None
    current_ts = None
    current_files = []

    for line in out.strip().split("\n"):
        line = line.strip()
        if not line:
            continue
        parts = line.split(" ", 1)
        if (
            len(parts) == 2
            and len(parts[0]) == 40
            and all(c in "0123456789abcdef" for c in parts[0])
        ):
            if current_hash is not None:
                entries.append((current_hash, current_ts, current_files))
            current_hash = parts[0]
            try:
                current_ts = int(parts[1])
            except ValueError:
                current_ts = 0
            current_files = []
        elif current_hash is not None:
            current_files.append(line)

    if current_hash is not None:
        entries.append((current_hash, current_ts, current_files))

    return entries


def bucket_into_windows(entries, known_files, window_seconds):
    """Bucket file changes into time windows."""
    if not entries:
        return {}, 0

    timestamps = [ts for _, ts, _ in entries if ts > 0]
    if not timestamps:
        return {}, 0

    min_ts = min(timestamps)
    max_ts = max(timestamps)
    n_windows = max(1, int((max_ts - min_ts) / window_seconds) + 1)

    file_series = defaultdict(lambda: [0] * n_windows)

    for _, ts, files in entries:
        if ts <= 0:
            continue
        bucket = min(int((ts - min_ts) / window_seconds), n_windows - 1)
        for f in files:
            if f in known_files:
                file_series[f][bucket] += 1

    return dict(file_series), n_windows


def linear_regression(ys):
    """Simple OLS: y = a + b*x. Returns (slope, r_squared)."""
    n = len(ys)
    if n < 2:
        return 0.0, 0.0

    xs = list(range(n))
    mean_x = sum(xs) / n
    mean_y = sum(ys) / n

    ss_xy = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys))
    ss_xx = sum((x - mean_x) ** 2 for x in xs)
    ss_yy = sum((y - mean_y) ** 2 for y in ys)

    if ss_xx == 0:
        return 0.0, 0.0

    slope = ss_xy / ss_xx
    r_squared = (ss_xy ** 2) / (ss_xx * ss_yy) if ss_yy > 0 else 0.0

    return slope, r_squared


def classify_trajectory(series):
    """Classify a churn time series into a trajectory type."""
    if not series:
        return "dormant"

    total = sum(series)
    if total == 0:
        return "dormant"

    n = len(series)
    mean_val = total / n
    variance = sum((v - mean_val) ** 2 for v in series) / n

    slope, r2 = linear_regression(series)

    # Coefficient of variation
    cv = (variance ** 0.5) / mean_val if mean_val > 0 else 0

    # Check for burst-then-stable: high first half, low second half
    if n >= 4:
        first_half = sum(series[: n // 2])
        second_half = sum(series[n // 2 :])
        if first_half > 0 and second_half / max(first_half, 1) < 0.3:
            return "burst-then-stable"

    if mean_val < 0.5:
        return "dormant"

    if slope < -0.05 and r2 > 0.2:
        return "stabilizing"

    if slope > 0.05 and r2 > 0.2:
        return "spiking"

    if cv > 1.0:
        return "churning"

    return "steady"


def sparkline(series):
    """Render a time series as an ASCII sparkline."""
    if not series:
        return ""
    max_val = max(series) if max(series) > 0 else 1
    chars = []
    for v in series:
        idx = int(v / max_val * (len(SPARKLINE_CHARS) - 1))
        idx = min(idx, len(SPARKLINE_CHARS) - 1)
        chars.append(SPARKLINE_CHARS[idx])
    return "".join(chars)


def main():
    codebase = sys.argv[1] if len(sys.argv) > 1 else "."
    codebase_path = Path(codebase).resolve()
    result, file_metrics = load_analysis(codebase)

    known_files = set(result.files.keys())

    print("=" * 72)
    print("EXPERIMENT 03 — CHURN TRAJECTORY ANALYSIS")
    print("=" * 72)
    print()

    entries = parse_git_log_with_time(codebase_path)
    if not entries:
        print("ERROR: No git history found.")
        return

    timestamps = [ts for _, ts, _ in entries if ts > 0]
    if not timestamps:
        print("ERROR: No valid timestamps in git history.")
        return

    repo_age_days = (max(timestamps) - min(timestamps)) / 86400
    print(f"Repository age: {repo_age_days:.0f} days")
    print(f"Total commits: {len(entries)}")

    # Choose window size based on repo age
    if repo_age_days > 365:
        window_seconds = 30 * 86400  # Monthly
        window_label = "monthly"
    elif repo_age_days > 60:
        window_seconds = 7 * 86400  # Weekly
        window_label = "weekly"
    else:
        window_seconds = max(1, int(repo_age_days / 10)) * 86400  # ~10 buckets
        window_label = f"{max(1, int(repo_age_days / 10))}-day"

    file_series, n_windows = bucket_into_windows(
        entries, known_files, window_seconds
    )

    print(f"Window size: {window_label} ({n_windows} windows)")
    print(f"Files with history: {len(file_series)}")
    print()

    # ── Classify each file ──────────────────────────────────────
    classifications = defaultdict(list)
    file_class = {}
    for f, series in file_series.items():
        cls = classify_trajectory(series)
        classifications[cls].append(f)
        file_class[f] = cls

    # Files with no git history at all
    for f in known_files:
        if f not in file_series:
            classifications["dormant"].append(f)

    print("1. TRAJECTORY CLASSIFICATION")
    print("-" * 72)
    for cls in ["spiking", "churning", "steady", "burst-then-stable", "stabilizing", "dormant"]:
        files = classifications.get(cls, [])
        marker = "!!" if cls in ("spiking", "churning") else "  "
        print(f"  {marker} {cls:<22} {len(files):>4} files")
    print()

    # ── Sparklines for interesting files ────────────────────────
    print("2. SPARKLINES — TOP CHURNING & SPIKING FILES")
    print("-" * 72)

    interesting = []
    for cls in ["spiking", "churning", "steady"]:
        for f in classifications.get(cls, []):
            total = sum(file_series.get(f, []))
            interesting.append((total, f, cls))

    interesting.sort(reverse=True)

    if not interesting:
        print("  No high-churn files found.")
    else:
        print(f"  {'File':<40} {'Type':<20} {'Total':>5} Sparkline")
        print(f"  {'-'*40} {'-'*20} {'-----':>5} ---------")
        for total, f, cls in interesting[:20]:
            series = file_series.get(f, [])
            sp = sparkline(series)
            short = f if len(f) <= 38 else "..." + f[-35:]
            print(f"  {short:<40} {cls:<20} {total:>5} {sp}")
    print()

    # ── Files that never stabilize ──────────────────────────────
    print("3. FILES THAT NEVER STABILIZE")
    print("-" * 72)
    never_stable = []
    for f in classifications.get("churning", []) + classifications.get("spiking", []):
        series = file_series.get(f, [])
        if series and n_windows >= 4:
            # Check if last quarter is still active
            last_q = series[-(n_windows // 4):]
            if sum(last_q) > 0:
                never_stable.append((sum(series), f))

    never_stable.sort(reverse=True)
    if not never_stable:
        print("  All high-churn files show recent stabilization.")
    else:
        for total, f in never_stable[:10]:
            series = file_series.get(f, [])
            sp = sparkline(series)
            short = f if len(f) <= 45 else "..." + f[-42:]
            print(f"  {short:<48} total={total:>3} {sp}")
    print()

    # ── Summary ─────────────────────────────────────────────────
    print("4. CHURN SUMMARY")
    print("-" * 72)
    total_changes = sum(sum(s) for s in file_series.values())
    top_file = max(file_series.items(), key=lambda x: sum(x[1]), default=(None, []))
    print(f"  Total file-changes: {total_changes}")
    if top_file[0]:
        print(f"  Most-changed file: {top_file[0]} ({sum(top_file[1])} changes)")
    n_concerning = len(classifications.get("spiking", [])) + len(classifications.get("churning", []))
    print(f"  Concerning trajectories: {n_concerning} files (spiking + churning)")
    print()


if __name__ == "__main__":
    main()
