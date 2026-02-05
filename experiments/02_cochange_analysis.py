#!/usr/bin/env python3
"""Experiment 02 — Process Mining: Co-Change Analysis.

Mines git log to build a co-change matrix, overlays on the structural
dependency graph, classifies file pairs into 4 quadrants, and computes
association rules (support, confidence, lift).
"""

import subprocess
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _bootstrap import load_analysis


def parse_git_log(codebase_path):
    """Parse git log to get commit -> files mapping."""
    cmd = [
        "git", "-C", str(codebase_path),
        "log", "--format=%H", "--name-only",
    ]
    try:
        out = subprocess.check_output(cmd, text=True, stderr=subprocess.DEVNULL)
    except (subprocess.CalledProcessError, FileNotFoundError):
        return {}

    commits = {}
    current_hash = None
    for line in out.strip().split("\n"):
        line = line.strip()
        if not line:
            continue
        if len(line) == 40 and all(c in "0123456789abcdef" for c in line):
            current_hash = line
            commits[current_hash] = []
        elif current_hash is not None:
            commits[current_hash].append(line)

    return commits


def build_cochange_matrix(commits, known_files):
    """Build co-change counts for pairs of known files."""
    pair_count = defaultdict(int)
    file_count = defaultdict(int)

    for _, files in commits.items():
        # Only consider files we know about
        relevant = [f for f in files if f in known_files]
        for f in relevant:
            file_count[f] += 1
        for i in range(len(relevant)):
            for j in range(i + 1, len(relevant)):
                a, b = min(relevant[i], relevant[j]), max(relevant[i], relevant[j])
                pair_count[(a, b)] += 1

    return pair_count, file_count


def main():
    codebase = sys.argv[1] if len(sys.argv) > 1 else "."
    codebase_path = Path(codebase).resolve()
    result, file_metrics = load_analysis(codebase)

    known_files = set(result.files.keys())
    graph = result.graph

    # Build structural edge set (undirected)
    structural_edges = set()
    for src, targets in graph.adjacency.items():
        for tgt in targets:
            a, b = min(src, tgt), max(src, tgt)
            structural_edges.add((a, b))

    print("=" * 72)
    print("EXPERIMENT 02 — CO-CHANGE ANALYSIS (PROCESS MINING)")
    print("=" * 72)
    print()

    # Parse git log
    commits = parse_git_log(codebase_path)
    if not commits:
        print("ERROR: No git history found. Run this on a git repository.")
        return

    print(f"Git history: {len(commits)} commits")
    print(f"Known files in analysis: {len(known_files)}")
    print(f"Structural dependency edges: {len(structural_edges)}")
    print()

    # Build co-change matrix
    pair_count, file_count = build_cochange_matrix(commits, known_files)
    total_commits = len(commits)

    # Jaccard-style co-change score
    cochange_scores = {}
    for (a, b), count in pair_count.items():
        union = file_count.get(a, 0) + file_count.get(b, 0) - count
        score = count / union if union > 0 else 0
        if count >= 2:  # Only consider pairs changed together at least twice
            cochange_scores[(a, b)] = score

    print(f"Co-change pairs (>= 2 co-commits): {len(cochange_scores)}")
    print()

    # ── 4-Quadrant Classification ───────────────────────────────
    cochange_set = set(cochange_scores.keys())
    threshold = 0.1  # Minimum Jaccard score to count as "co-changing"

    strong_cochange = {p for p, s in cochange_scores.items() if s >= threshold}

    expected = structural_edges & strong_cochange
    dead_dep = structural_edges - strong_cochange
    hidden_coupling = strong_cochange - structural_edges

    print("1. FOUR-QUADRANT CLASSIFICATION")
    print("-" * 72)
    print(f"  Expected (structural + co-change):   {len(expected):>5}")
    print(f"  Possibly dead dependency (struct only): {len(dead_dep):>5}")
    print(f"  Hidden coupling (co-change only):      {len(hidden_coupling):>5}")
    print(f"  Independent (neither):                 {'  ...'}")
    print()

    # ── Top Hidden Couplings ────────────────────────────────────
    print("2. TOP HIDDEN COUPLINGS (co-change without structural dependency)")
    print("-" * 72)
    hidden_sorted = sorted(hidden_coupling, key=lambda p: cochange_scores.get(p, 0), reverse=True)
    if not hidden_sorted:
        print("  None found.")
    else:
        print(f"  {'File A':<35} {'File B':<35} Score")
        print(f"  {'-'*35} {'-'*35} -----")
        for a, b in hidden_sorted[:15]:
            score = cochange_scores[(a, b)]
            sa = a if len(a) <= 33 else "..." + a[-30:]
            sb = b if len(b) <= 33 else "..." + b[-30:]
            print(f"  {sa:<35} {sb:<35} {score:.3f}")
    print()

    # ── Top Dead Dependencies ───────────────────────────────────
    print("3. POSSIBLY DEAD DEPENDENCIES (structural edge, never co-change)")
    print("-" * 72)
    truly_dead = [(a, b) for a, b in dead_dep if pair_count.get((a, b), 0) == 0]
    if not truly_dead:
        print("  None — all structural deps have at least some co-change.")
    else:
        for a, b in truly_dead[:15]:
            sa = a if len(a) <= 33 else "..." + a[-30:]
            sb = b if len(b) <= 33 else "..." + b[-30:]
            print(f"  {sa:<35} → {sb}")
        if len(truly_dead) > 15:
            print(f"  ... and {len(truly_dead) - 15} more")
    print()

    # ── Association Rules ───────────────────────────────────────
    print("4. ASSOCIATION RULES (support, confidence, lift)")
    print("-" * 72)
    print(f"  {'A => B':<55} {'Supp':>6} {'Conf':>6} {'Lift':>6}")
    print(f"  {'-'*55} {'-----':>6} {'-----':>6} {'-----':>6}")

    rules = []
    for (a, b), count in pair_count.items():
        if count < 2:
            continue
        support = count / total_commits
        # Confidence: P(B|A) = P(A,B) / P(A)
        conf_ab = count / file_count[a] if file_count[a] > 0 else 0
        conf_ba = count / file_count[b] if file_count[b] > 0 else 0
        # Lift: confidence / P(B)
        p_b = file_count[b] / total_commits if total_commits > 0 else 0
        p_a = file_count[a] / total_commits if total_commits > 0 else 0
        lift_ab = conf_ab / p_b if p_b > 0 else 0
        lift_ba = conf_ba / p_a if p_a > 0 else 0

        # Use the direction with higher confidence
        if conf_ab >= conf_ba:
            rules.append((a, b, support, conf_ab, lift_ab))
        else:
            rules.append((b, a, support, conf_ba, lift_ba))

    rules.sort(key=lambda r: r[4], reverse=True)  # Sort by lift
    for a, b, supp, conf, lift in rules[:20]:
        sa = Path(a).name
        sb = Path(b).name
        label = f"{sa} => {sb}"
        if len(label) > 53:
            label = label[:50] + "..."
        print(f"  {label:<55} {supp:>6.3f} {conf:>6.2f} {lift:>6.1f}")

    print()

    # ── Summary ─────────────────────────────────────────────────
    print("5. SUMMARY")
    print("-" * 72)
    if hidden_coupling:
        print(f"  {len(hidden_coupling)} hidden couplings suggest files that change together")
        print("  but have no import relationship — consider whether they should.")
    if truly_dead:
        print(f"  {len(truly_dead)} structural dependencies never co-change — may be dead code.")
    print()


if __name__ == "__main__":
    main()
